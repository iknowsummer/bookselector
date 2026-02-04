import logging

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..exceptions import handle_database_error
from ..models import Book, UserBook
from ..schemas import BookStatus, UserBookCreate, UserBookUpdate

logger = logging.getLogger(__name__)


def create_user_book(
    payload: UserBookCreate,
    user_id: int,
    db: Session,
) -> UserBook:
    logger.info(f"POST /user-books - Creating user book for user_id={user_id}")

    try:
        book = db.query(Book).filter(Book.id == payload.book_id).first()
        if not book:
            logger.warning("POST /user-books - Book not found (404)")
            raise HTTPException(status_code=404, detail="Book not found")

        existing = (
            db.query(UserBook)
            .filter(UserBook.user_id == user_id, UserBook.book_id == payload.book_id)
            .first()
        )
        if existing:
            logger.warning("POST /user-books - UserBook already exists (409)")
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

        logger.info(
            f"POST /user-books - Successfully created user_book id={user_book.id}"
        )
        return user_book

    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"POST /user-books - Database error: {str(exc)}", exc_info=True)
        raise handle_database_error(exc, "user book creation") from exc


def update_user_book(
    book_id: int,
    payload: UserBookUpdate,
    user_id: int,
    db: Session,
) -> UserBook:
    logger.info(f"PUT /user-books/{book_id} - Updating user book for user_id={user_id}")

    try:
        user_book = (
            db.query(UserBook)
            .filter(UserBook.user_id == user_id, UserBook.book_id == book_id)
            .first()
        )

        if not user_book:
            logger.warning(f"PUT /user-books/{book_id} - UserBook not found (404)")
            raise HTTPException(status_code=404, detail="UserBook not found")

        for key, value in payload.model_dump(exclude_unset=True).items():
            if key == "status" and isinstance(value, BookStatus):
                setattr(user_book, key, value.value)
            elif value is not None:
                setattr(user_book, key, value)

        db.commit()
        db.refresh(user_book)

        logger.info(f"PUT /user-books/{book_id} - Successfully updated user_book")
        return user_book

    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(
            f"PUT /user-books/{book_id} - Database error: {str(exc)}", exc_info=True
        )
        raise handle_database_error(exc, "user book update") from exc


def delete_user_book(
    book_id: int,
    user_id: int,
    db: Session,
) -> dict:
    logger.info(
        f"DELETE /user-books/{book_id} - Deleting user book for user_id={user_id}"
    )

    try:
        user_book = (
            db.query(UserBook)
            .filter(UserBook.user_id == user_id, UserBook.book_id == book_id)
            .first()
        )

        if not user_book:
            logger.warning(f"DELETE /user-books/{book_id} - UserBook not found (404)")
            raise HTTPException(status_code=404, detail="UserBook not found")

        db.delete(user_book)
        db.commit()

        logger.info(f"DELETE /user-books/{book_id} - Successfully deleted user_book")
        return {"message": "UserBook deleted successfully"}

    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(
            f"DELETE /user-books/{book_id} - Database error: {str(exc)}", exc_info=True
        )
        raise handle_database_error(exc, "user book deletion") from exc
