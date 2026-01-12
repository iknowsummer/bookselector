import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserRead, UserUpdate
from ..exceptions import handle_database_error, handle_internal_error

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/users/", response_model=list[UserRead])
def read_users(db: Session = Depends(get_db)):
    """ユーザー一覧を取得"""
    logger.info("GET /users - Fetching user list")
    users = db.query(User).order_by(User.id.asc()).all()
    logger.info("GET /users - Retrieved %s users", len(users))
    return users


@router.get("/users/{user_id}", response_model=UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """ユーザー詳細を取得"""
    logger.info("GET /users/%s - Fetching user detail", user_id)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning("GET /users/%s - User not found", user_id)
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """ユーザーを新規作成"""
    logger.info("POST /users - Creating user: name='%s'", user.name)
    if not user.auth0_sub or not user.email:
        raise HTTPException(
            status_code=400,
            detail="auth0_sub と email は必須です"
        )
    try:
        db_user = User(**user.model_dump())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info("POST /users - Created user id=%s", db_user.id)
        return db_user
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("POST /users - Database error: %s", exc, exc_info=True)
        raise handle_database_error(exc, "user creation") from exc
    except Exception as exc:  # 念のため予期しない例外を補足
        db.rollback()
        logger.error("POST /users - Unexpected error: %s", exc, exc_info=True)
        raise handle_internal_error(exc, "user creation") from exc


@router.put("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """ユーザー情報を更新"""
    logger.info("PUT /users/%s - Updating user", user_id)
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            logger.warning("PUT /users/%s - User not found", user_id)
            raise HTTPException(status_code=404, detail="User not found")

        for key, value in user.model_dump(exclude_unset=True).items():
            setattr(db_user, key, value)

        db.commit()
        db.refresh(db_user)
        logger.info("PUT /users/%s - Updated user", user_id)
        return db_user
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("PUT /users/%s - Database error: %s", user_id, exc, exc_info=True)
        raise handle_database_error(exc, "user update") from exc


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """ユーザーを削除"""
    logger.info("DELETE /users/%s - Deleting user", user_id)
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning("DELETE /users/%s - User not found", user_id)
            raise HTTPException(status_code=404, detail="User not found")

        db.delete(user)
        db.commit()
        logger.info("DELETE /users/%s - Deleted user", user_id)
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("DELETE /users/%s - Database error: %s", user_id, exc, exc_info=True)
        raise handle_database_error(exc, "user deletion") from exc
