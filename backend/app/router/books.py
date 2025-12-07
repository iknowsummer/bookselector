import os
import logging

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from sqlalchemy.exc import SQLAlchemyError

from ..database import get_db
from ..context import CurrentUser
from ..models import Book, UserBook
from ..schemas import BookCreate, BookRead, BookUpdate, BookStatus
from ..exceptions import (
    handle_database_error,
    handle_internal_error,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _build_book_response(book: Book, user_book: UserBook | None) -> dict:
    """
    Book と UserBook を結合して BookRead 互換の辞書を作成
    """
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "description": book.description,
        "target_age": book.target_age,
        "isbn": book.isbn,
        "image_url": book.image_url,
        "created_at": book.created_at,
        "note": user_book.note if user_book else None,
        "status": user_book.status if user_book else BookStatus.UNREAD.value,
        "shelf_id": user_book.shelf_id if user_book else None,
    }


@router.get("/books/random", response_model=list[BookRead])
def random_books(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    include_all_status: int = Query(0, description="1で全ステータスを含める。デフォルトはunreadのみ。"),
):
    logger.info(
        f"GET /books/random - user_id={current_user.id}, include_all_status={include_all_status}"
    )

    try:
        pickcount = int(os.getenv("PICKCOUNT", "4"))

        # Book と UserBook を JOIN
        query = (
            db.query(Book, UserBook)
            .join(UserBook, Book.id == UserBook.book_id)
            .filter(UserBook.user_id == current_user.id)
        )

        # ステータスフィルタリング
        if include_all_status == 0:
            query = query.filter(UserBook.status == BookStatus.UNREAD.value)

        results = query.order_by(func.random()).limit(pickcount).all()
        books = [_build_book_response(book, user_book) for book, user_book in results]

        logger.info(f"GET /books/random - Retrieved {len(books)} books")
        return books

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"GET /books/random - Unexpected error: {str(exc)}", exc_info=True)
        raise handle_internal_error(exc, "random book selection")


@router.post("/books/", response_model=BookRead)
def create_book(
    book: BookCreate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    logger.info(f"POST /books - Creating book: title='{book.title}' for user_id={current_user.id}")

    try:
        # BookCreate から Book フィールドと UserBook フィールドを分離
        book_data = book.model_dump()
        user_book_data = {
            "note": book_data.pop("note", None),
            "status": book_data.pop("status", BookStatus.UNREAD).value if isinstance(book_data.get("status"), BookStatus) else book_data.pop("status", BookStatus.UNREAD.value),
            "shelf_id": book_data.pop("shelf_id", None),
        }

        # Book 作成
        db_book = Book(**book_data)
        db.add(db_book)
        db.flush()  # ID を取得

        # UserBook 作成
        db_user_book = UserBook(
            user_id=current_user.id,
            book_id=db_book.id,
            **user_book_data
        )
        db.add(db_user_book)
        db.commit()
        db.refresh(db_book)
        db.refresh(db_user_book)

        logger.info(f"POST /books - Successfully created book id={db_book.id}")
        return _build_book_response(db_book, db_user_book)

    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"POST /books - Database error: {str(exc)}", exc_info=True)
        raise handle_database_error(exc, "book creation") from exc


@router.get("/books/", response_model=list[BookRead])
def read_books(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    limit: int | None = Query(None, description="取得件数の上限"),
    order_by: str = Query("created_at", description="ソート対象のフィールド"),
    order: str = Query("desc", description="ソート順序 (desc or asc)"),
    shelf_id: int | None = Query(None, description="特定の棚に所属する本のみを取得"),
    unassigned_only: bool = Query(False, description="棚未登録の本のみを取得"),
):
    logger.info(
        f"GET /books - user_id={current_user.id}, limit={limit}, order_by='{order_by}', "
        f"order='{order}', shelf_id={shelf_id}, unassigned_only={unassigned_only}"
    )

    # Book と UserBook を JOIN
    query = (
        db.query(Book, UserBook)
        .join(UserBook, Book.id == UserBook.book_id)
        .filter(UserBook.user_id == current_user.id)
    )

    # 棚IDでフィルタリング（UserBook.shelf_id を使用）
    if unassigned_only:
        query = query.filter(UserBook.shelf_id.is_(None))
    elif shelf_id is not None:
        query = query.filter(UserBook.shelf_id == shelf_id)

    # ソート処理（UserBook のカラムを優先）
    if hasattr(UserBook, order_by):
        order_column = getattr(UserBook, order_by)
    elif hasattr(Book, order_by):
        order_column = getattr(Book, order_by)
    else:
        order_column = UserBook.created_at

    if order.lower() == "desc":
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column.asc())

    if limit is not None:
        query = query.limit(limit)

    results = query.all()
    books = [_build_book_response(book, user_book) for book, user_book in results]

    logger.info(f"GET /books - Retrieved {len(books)} books")
    return books


@router.get("/books/{id}", response_model=BookRead)
def read_book(
    id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    指定されたIDの書籍を取得
    """
    logger.info(f"GET /books/{id} - Fetching book for user_id={current_user.id}")

    result = (
        db.query(Book, UserBook)
        .join(UserBook, Book.id == UserBook.book_id)
        .filter(
            Book.id == id,
            UserBook.user_id == current_user.id
        )
        .first()
    )

    if not result:
        logger.warning(f"GET /books/{id} - Book not found (404)")
        raise HTTPException(status_code=404, detail="Book not found")

    book, user_book = result
    logger.info(f"GET /books/{id} - Successfully retrieved book")
    return _build_book_response(book, user_book)


@router.put("/books/{id}", response_model=BookRead)
def update_book(
    id: int,
    book: BookUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    logger.info(f"PUT /books/{id} - Updating book for user_id={current_user.id}")

    try:
        # Book と UserBook を取得
        result = (
            db.query(Book, UserBook)
            .join(UserBook, Book.id == UserBook.book_id)
            .filter(
                Book.id == id,
                UserBook.user_id == current_user.id
            )
            .first()
        )

        if not result:
            logger.warning(f"PUT /books/{id} - Book not found (404)")
            raise HTTPException(status_code=404, detail="Book not found")

        db_book, db_user_book = result

        # Book フィールドと UserBook フィールドを分離して更新
        book_fields = {"title", "author", "description", "target_age", "isbn", "image_url"}
        user_book_fields = {"note", "status", "shelf_id"}

        for key, value in book.model_dump(exclude_unset=True).items():
            if key in book_fields and value is not None:
                setattr(db_book, key, value)
            elif key in user_book_fields:
                if key == "status" and isinstance(value, BookStatus):
                    setattr(db_user_book, key, value.value)
                elif value is not None:
                    setattr(db_user_book, key, value)

        db.commit()
        db.refresh(db_book)
        db.refresh(db_user_book)

        logger.info(f"PUT /books/{id} - Successfully updated book")
        return _build_book_response(db_book, db_user_book)

    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"PUT /books/{id} - Database error: {str(exc)}", exc_info=True)
        raise handle_database_error(exc, "book update") from exc


@router.delete("/books/{id}")
def delete_book(
    id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    logger.info(f"DELETE /books/{id} - Deleting book for user_id={current_user.id}")

    try:
        # UserBook を取得
        user_book = (
            db.query(UserBook)
            .filter(
                UserBook.book_id == id,
                UserBook.user_id == current_user.id
            )
            .first()
        )

        if not user_book:
            logger.warning(f"DELETE /books/{id} - Book not found (404)")
            raise HTTPException(status_code=404, detail="Book not found")

        # UserBook のみ削除（Book は残す）
        db.delete(user_book)
        db.commit()

        logger.info(f"DELETE /books/{id} - Successfully deleted book")
        return {"message": "Book deleted successfully"}

    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"DELETE /books/{id} - Database error: {str(exc)}", exc_info=True)
        raise handle_database_error(exc, "book deletion") from exc


@router.patch("/books/{id}/status", response_model=BookRead)
def update_book_status(
    id: int,
    current_user: CurrentUser,
    status: BookStatus = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    """
    書籍のステータスを更新

    status: "unread", "picked", "read" のいずれか
    """
    logger.info(f"PATCH /books/{id}/status - Updating status to '{status.value}' for user_id={current_user.id}")

    try:
        result = (
            db.query(Book, UserBook)
            .join(UserBook, Book.id == UserBook.book_id)
            .filter(
                Book.id == id,
                UserBook.user_id == current_user.id
            )
            .first()
        )

        if not result:
            logger.warning(f"PATCH /books/{id}/status - Book not found (404)")
            raise HTTPException(status_code=404, detail="Book not found")

        book, user_book = result
        user_book.status = status.value  # UserBook.status を更新

        db.commit()
        db.refresh(book)
        db.refresh(user_book)

        logger.info(f"PATCH /books/{id}/status - Successfully updated status")
        return _build_book_response(book, user_book)

    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"PATCH /books/{id}/status - Database error: {str(exc)}", exc_info=True)
        raise handle_database_error(exc, "book status update") from exc
