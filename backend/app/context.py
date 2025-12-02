"""APIリクエストのユーザーコンテキスト管理"""
import logging
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import User

logger = logging.getLogger(__name__)


def get_current_user(db: Session = Depends(get_db)) -> User:
    """
    現在のユーザーコンテキストを取得する。
    現在の実装: 常に管理者ユーザー（id=1）を返す。存在しない場合は自動作成する。
    認証実装後: 認証情報から実際のユーザーを判定する。

    Returns:
        User: 現在のユーザー（現在は管理者のみ）

    Raises:
        RuntimeError: 管理者ユーザーの作成/取得に失敗した場合
    """
    user = db.query(User).filter(User.id == 1).first()

    if not user:
        # 最初のアクセス時に管理者ユーザーを自動作成
        user = User(id=1, name="admin")
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("管理者ユーザー（id=1）を自動作成しました")

    return user


# 依存性注入用の型エイリアス
CurrentUser = Annotated[User, Depends(get_current_user)]
