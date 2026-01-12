"""APIリクエストのユーザーコンテキスト管理"""
import logging
from datetime import datetime, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .database import get_db
from .models import User

logger = logging.getLogger(__name__)


def _extract_auth0_identity(request: Request) -> tuple[str, str]:
    auth0_sub = request.headers.get("X-Auth0-Sub")
    email = request.headers.get("X-Auth0-Email")

    if not auth0_sub:
        raise HTTPException(status_code=401, detail="認証情報がありません")
    if not email:
        raise HTTPException(status_code=400, detail="メールアドレスがありません")

    return auth0_sub, email


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    現在のユーザーコンテキストを取得する。
    認証情報の sub を使ってユーザーを取得し、未登録なら自動作成する。

    Returns:
        User: 現在のユーザー

    Raises:
        HTTPException: 認証情報が不足している場合
    """
    auth0_sub, email = _extract_auth0_identity(request)
    user = db.query(User).filter(User.auth0_sub == auth0_sub).first()

    if not user:
        user = User(
            auth0_sub=auth0_sub,
            email=email,
            name=email,
            created_at=datetime.now(timezone.utc)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("ユーザーを新規作成しました: %s", auth0_sub)

    return user


# 依存性注入用の型エイリアス
CurrentUser = Annotated[User, Depends(get_current_user)]
