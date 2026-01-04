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
from ..lookup import fetch_book_by_isbn

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
    logger.info(f"POST /books - Creating book: isbn='{book.isbn}' for user_id={current_user.id}")

    try:
        existing_book = db.query(Book).filter(Book.isbn == book.isbn).first()
        if existing_book:
            logger.info(f"POST /books - Existing book found for isbn='{book.isbn}'")
            return _build_book_response(existing_book, None)

        book_info = fetch_book_by_isbn(book.isbn)

        # BookCreate から Book フィールドと UserBook フィールドを分離
        book_data = {
            "title": book_info.title,
            "author": book_info.author,
            "description": book_info.description,
            "isbn": book_info.isbn,
            "image_url": book_info.image_url,
        }

        # Book 作成
        db_book = Book(**book_data)
        db.add(db_book)
        db.commit()
        db.refresh(db_book)

        logger.info(f"POST /books - Successfully created book id={db_book.id}")
        return _build_book_response(db_book, None)

    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"POST /books - Database error: {str(exc)}", exc_info=True)
        raise handle_database_error(exc, "book creation") from exc


@router.get("/books/", response_model=list[BookRead])
def read_books(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    limit: int | None = Query(None, description="取得件数の上限"),
    order_by: str | None = Query(None, description="ソート対象のフィールド"),
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

    # ソート処理（デフォルトは user_books の登録日）
    if order_by is None:
        order_column = UserBook.created_at
    elif order_by == "created_at":
        order_column = UserBook.created_at
    elif hasattr(UserBook, order_by):
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

    raise HTTPException(status_code=400, detail="書籍情報は更新できません")


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
