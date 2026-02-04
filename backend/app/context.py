"""APIリクエストのユーザーコンテキスト管理"""

from typing import Annotated
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .auth import jwt_bearer


def get_current_user(
    token_payload: dict = Depends(jwt_bearer), db: Session = Depends(get_db)
) -> User:
    """
    JWTトークンから現在のユーザーを取得または作成する。

    Auth0のsubクレームをユーザー識別子として使用。
    初回アクセス時はユーザーを自動作成。

    Args:
        token_payload: JWT検証済みペイロード（jwt_bearerからの依存性注入）
        db: データベースセッション

    Returns:
        User: 現在のユーザーオブジェクト

    Raises:
        HTTPException: ユーザー作成/取得に失敗した場合
    """
    auth0_sub = token_payload.get("sub")

    if not auth0_sub:
        raise HTTPException(status_code=401, detail="ユーザー識別子がありません")

    # auth0_subでユーザーを検索
    user = db.query(User).filter(User.auth0_sub == auth0_sub).first()

    if not user:
        # 初回アクセス時にユーザーを自動作成
        # JWTペイロードからメールアドレスを取得（あれば）
        email = token_payload.get("email")
        # nameはAuth0の設定によりnickname, name, emailなど様々
        name = (
            token_payload.get("name")
            or token_payload.get("nickname")
            or token_payload.get("email")
            or "User"
        )

        try:
            user = User(auth0_sub=auth0_sub, name=name, email=email)
            db.add(user)
            db.commit()
            db.refresh(user)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="ユーザーの作成に失敗しました")

    return user


# 依存性注入用の型エイリアス
CurrentUser = Annotated[User, Depends(get_current_user)]
