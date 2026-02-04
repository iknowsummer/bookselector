from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..exceptions import handle_database_error
from ..models import Book, UserBook
from ..schemas import BookStatus, UserBookCreate, UserBookUpdate


def create_user_book(
    payload: UserBookCreate,
    user_id: int,
    db: Session,
) -> UserBook:
    try:
        book = db.query(Book).filter(Book.id == payload.book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        existing = (
            db.query(UserBook)
            .filter(UserBook.user_id == user_id, UserBook.book_id == payload.book_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=409, detail="UserBook already exists")

        user_book = UserBook(
            user_id=user_id,
            book_id=payload.book_id,
            note=payload.note,
            status=payload.status.value
            if isinstance(payload.status, BookStatus)
            else payload.status,
            shelf_id=payload.shelf_id,
        )
        db.add(user_book)
        db.commit()
        db.refresh(user_book)

        return user_book

    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise handle_database_error(exc, "user book creation") from exc


def update_user_book(
    book_id: int,
    payload: UserBookUpdate,
    user_id: int,
    db: Session,
) -> UserBook:
    try:
        user_book = (
            db.query(UserBook)
            .filter(UserBook.user_id == user_id, UserBook.book_id == book_id)
            .first()
        )

        if not user_book:
            raise HTTPException(status_code=404, detail="UserBook not found")

        for key, value in payload.model_dump(exclude_unset=True).items():
            if key == "status" and isinstance(value, BookStatus):
                setattr(user_book, key, value.value)
            elif value is not None:
                setattr(user_book, key, value)

        db.commit()
        db.refresh(user_book)

        return user_book

    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise handle_database_error(exc, "user book update") from exc


def delete_user_book(
    book_id: int,
    user_id: int,
    db: Session,
) -> dict:
    try:
        user_book = (
            db.query(UserBook)
            .filter(UserBook.user_id == user_id, UserBook.book_id == book_id)
            .first()
        )

        if not user_book:
            raise HTTPException(status_code=404, detail="UserBook not found")

        db.delete(user_book)
        db.commit()

        return {"message": "UserBook deleted successfully"}

    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise handle_database_error(exc, "user book deletion") from exc
