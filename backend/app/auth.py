import logging
import os
import time

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTClaimsError, JWTError, jwt

logger = logging.getLogger(__name__)

security = HTTPBearer()

_JWKS_CACHE: dict | None = None
_JWKS_CACHE_EXPIRES_AT = 0.0
_JWKS_CACHE_TTL = 60 * 60


def _get_auth0_settings() -> tuple[str, str]:
    domain = os.getenv("AUTH0_DOMAIN")
    audience = os.getenv("AUTH0_AUDIENCE")
    if not domain or not audience:
        logger.error("Auth0の設定が不足しています。AUTH0_DOMAIN/AUTH0_AUDIENCEを確認してください。")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth0の設定が不足しています。",
        )
    return domain, audience


def _fetch_jwks(domain: str) -> dict:
    global _JWKS_CACHE
    global _JWKS_CACHE_EXPIRES_AT

    now = time.time()
    if _JWKS_CACHE and now < _JWKS_CACHE_EXPIRES_AT:
        return _JWKS_CACHE

    jwks_url = f"https://{domain}/.well-known/jwks.json"
    try:
        response = httpx.get(jwks_url, timeout=10.0)
        response.raise_for_status()
        jwks = response.json()
    except httpx.HTTPError as exc:
        logger.error("JWKSの取得に失敗しました: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWKSの取得に失敗しました。",
        ) from exc

    _JWKS_CACHE = jwks
    _JWKS_CACHE_EXPIRES_AT = now + _JWKS_CACHE_TTL
    return jwks


def _find_rsa_key(jwks: dict, token_header: dict) -> dict | None:
    for key in jwks.get("keys", []):
        if key.get("kid") == token_header.get("kid"):
            return {
                "kty": key.get("kty"),
                "kid": key.get("kid"),
                "use": key.get("use"),
                "n": key.get("n"),
                "e": key.get("e"),
            }
    return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    domain, audience = _get_auth0_settings()
    token = credentials.credentials
    issuer = f"https://{domain}/"

    try:
        token_header = jwt.get_unverified_header(token)
    except JWTError as exc:
        logger.warning("トークンヘッダーの解析に失敗しました: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです。",
        ) from exc

    jwks = _fetch_jwks(domain)
    rsa_key = _find_rsa_key(jwks, token_header)
    if not rsa_key:
        logger.warning("対応する公開鍵が見つかりません。")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです。",
        )

    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=audience,
            issuer=issuer,
        )
    except ExpiredSignatureError as exc:
        logger.info("トークンの有効期限が切れています。")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンの有効期限が切れています。",
        ) from exc
    except JWTClaimsError as exc:
        logger.info("トークンのクレーム検証に失敗しました: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンの検証に失敗しました。",
        ) from exc
    except JWTError as exc:
        logger.info("トークンの検証に失敗しました: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンの検証に失敗しました。",
        ) from exc

    sub = payload.get("sub")
    email = payload.get("email")
    if not sub:
        logger.warning("トークンにsubが含まれていません。")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンの検証に失敗しました。",
        )

    return {"sub": sub, "email": email}
