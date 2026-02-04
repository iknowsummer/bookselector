"""アクセスログミドルウェア"""

import logging
import time
import uuid
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("access")

# 認証をスキップするパス（プレフィックスマッチ）
SKIP_AUTH_PATHS = [
    "/health",
    "/db-status",
    "/lookup/",
    "/docs",
    "/openapi.json",
    "/redoc",
]


class AccessLogMiddleware(BaseHTTPMiddleware):
    """
    アクセスログを一元管理するミドルウェア

    機能:
    - リクエスト/レスポンスのログ出力
    - ユーザー識別子（auth0_sub）の紐付け
    - リクエストIDの生成
    - 処理時間の計測
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # リクエストIDを生成
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # 開始時刻を記録
        start_time = time.perf_counter()

        # JWT検証（認証が必要なパスの場合）
        user_sub = await self._extract_user_sub(request)

        # クライアントIP取得
        client_ip = self._get_client_ip(request)

        try:
            response = await call_next(request)

            # 処理時間を計算
            duration_ms = (time.perf_counter() - start_time) * 1000

            # アクセスログ出力
            self._log_request(
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                user_sub=user_sub,
                status_code=response.status_code,
                duration_ms=duration_ms,
                client_ip=client_ip,
            )

            return response

        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self._log_request(
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                user_sub=user_sub,
                status_code=500,
                duration_ms=duration_ms,
                client_ip=client_ip,
                error=str(exc),
            )
            raise

    async def _extract_user_sub(self, request: Request) -> Optional[str]:
        """
        リクエストからユーザー識別子（auth0_sub）を抽出

        JWT検証を行い、成功した場合はペイロードを request.state に保存
        """
        # 認証スキップパスの場合
        if self._should_skip_auth(request.url.path):
            request.state.jwt_payload = None
            return None

        # Authorization ヘッダーを取得
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            request.state.jwt_payload = None
            return None

        token = auth_header.split(" ", 1)[1]

        try:
            from ..auth import verify_token_safe

            payload = verify_token_safe(token)

            if payload:
                request.state.jwt_payload = payload
                return payload.get("sub")

        except Exception:
            pass

        request.state.jwt_payload = None
        return None

    def _should_skip_auth(self, path: str) -> bool:
        """認証をスキップするパスかどうか判定"""
        return any(path.startswith(skip_path) for skip_path in SKIP_AUTH_PATHS)

    def _get_client_ip(self, request: Request) -> str:
        """クライアントIPを取得（プロキシ対応）"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _log_request(
        self,
        request_id: str,
        method: str,
        path: str,
        user_sub: Optional[str],
        status_code: int,
        duration_ms: float,
        client_ip: str,
        error: Optional[str] = None,
    ):
        """アクセスログを出力"""
        user_str = f"user={user_sub}" if user_sub else "user=anonymous"

        log_message = (
            f"[{request_id}] {method} {path} - {user_str} - "
            f"{status_code} - {duration_ms:.1f}ms - {client_ip}"
        )

        if error:
            log_message += f" - error={error}"

        # ステータスコードに応じてログレベルを変更
        if status_code >= 500:
            logger.error(log_message)
        elif status_code >= 400:
            logger.warning(log_message)
        else:
            logger.info(log_message)
