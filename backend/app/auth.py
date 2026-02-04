"""Auth0 JWT認証設定と検証"""

import os
import logging
from functools import lru_cache
from typing import Optional

import jwt
from jwt import PyJWKClient
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)


@lru_cache()
def get_auth_config() -> dict:
    """Auth0設定を取得（キャッシュ付き）"""
    return {
        "domain": os.getenv("AUTH0_DOMAIN", ""),
        "audience": os.getenv("AUTH0_AUDIENCE", ""),
        "algorithms": ["RS256"],
    }


@lru_cache()
def get_jwks_client() -> PyJWKClient:
    """JWKSクライアントを取得（5分間キャッシュ）

    PyJWKClientは内部でJWKSをキャッシュするため、
    毎回Auth0にリクエストを送ることはない。
    """
    config = get_auth_config()
    jwks_url = f"https://{config['domain']}/.well-known/jwks.json"
    return PyJWKClient(jwks_url, cache_keys=True)


class JWTBearer(HTTPBearer):
    """JWT認証用のHTTPBearerスキーム"""

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[dict]:
        """
        リクエストからJWTを抽出して検証

        Returns:
            dict: 検証済みのJWTペイロード（sub, email等を含む）

        Raises:
            HTTPException: 認証失敗時
        """
        # ミドルウェアで検証済みの場合はスキップ
        if hasattr(request.state, "jwt_payload") and request.state.jwt_payload:
            return request.state.jwt_payload

        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(
            request
        )

        if credentials is None:
            raise HTTPException(status_code=401, detail="認証トークンがありません")

        if credentials.scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Bearer認証が必要です")

        return self._verify_token(credentials.credentials)

    def _verify_token(self, token: str) -> dict:
        """
        JWTトークンを検証

        Args:
            token: JWT文字列

        Returns:
            dict: デコードされたペイロード

        Raises:
            HTTPException: 検証失敗時
        """
        config = get_auth_config()

        try:
            # JWKSからsigning keyを取得
            jwks_client = get_jwks_client()
            signing_key = jwks_client.get_signing_key_from_jwt(token)

            # トークンを検証・デコード
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=config["algorithms"],
                audience=config["audience"],
                issuer=f"https://{config['domain']}/",
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iss": True,
                    "verify_aud": True,
                },
            )

            logger.debug(f"JWT検証成功: sub={payload.get('sub')}")
            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("JWT検証失敗: トークン有効期限切れ")
            raise HTTPException(
                status_code=401, detail="トークンの有効期限が切れています"
            )

        except jwt.InvalidAudienceError:
            logger.warning("JWT検証失敗: 不正なaudience")
            raise HTTPException(status_code=401, detail="トークンのaudienceが不正です")

        except jwt.InvalidIssuerError:
            logger.warning("JWT検証失敗: 不正なissuer")
            raise HTTPException(status_code=401, detail="トークンのissuerが不正です")

        except jwt.PyJWKClientError as e:
            logger.error(f"JWKS取得エラー: {e}")
            raise HTTPException(status_code=401, detail="認証キーの取得に失敗しました")

        except jwt.DecodeError as e:
            logger.warning(f"JWTデコードエラー: {e}")
            raise HTTPException(status_code=401, detail="トークンの形式が不正です")

        except Exception as e:
            logger.error(f"JWT検証で予期せぬエラー: {e}", exc_info=True)
            raise HTTPException(status_code=401, detail="認証に失敗しました")


# シングルトンインスタンス
jwt_bearer = JWTBearer()


def verify_token_safe(token: str) -> Optional[dict]:
    """
    例外を投げずにJWT検証を行う（ミドルウェア用）

    Returns:
        dict: 検証成功時のペイロード
        None: 検証失敗時
    """
    try:
        return jwt_bearer._verify_token(token)
    except Exception:
        return None
