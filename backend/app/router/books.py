import os
import logging

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from sqlalchemy.exc import SQLAlchemyError

from ..database import get_db
from ..models import Book
from ..schemas import BookCreate, BookRead, BookUpdate, BookStatus
from ..exceptions import (
    handle_database_error,
    handle_internal_error,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/books/random", response_model=list[BookRead])
def random_books(
    db: Session = Depends(get_db),
    include_all_status: int = Query(0, description="1で全ステータスを含める。デフォルトはunreadのみ。"),
):
    logger.info(f"GET /books/random - include_all_status={include_all_status}")

    try:
        pickcount = int(os.getenv("PICKCOUNT", "4"))

        # クエリ実行
        if include_all_status == 0:
            query = db.query(Book).filter(Book.status == BookStatus.UNREAD.value)
        else:
            query = db.query(Book)

        books = query.order_by(func.random()).limit(pickcount).all()
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
    db: Session = Depends(get_db),
):
    logger.info(f"POST /books - Creating book: title='{book.title}'")

    try:
        db_book = Book(**book.dict())
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        logger.info(f"POST /books - Successfully created book with id={db_book.id}")
        return db_book
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"POST /books - Database error: {str(exc)}", exc_info=True)
        raise handle_database_error(exc, "book creation") from exc


@router.get("/books/", response_model=list[BookRead])
def read_books(
    limit: int | None = Query(None, description="取得件数の上限"),
    order_by: str = Query("created_at", description="ソート対象のフィールド"),
    order: str = Query("desc", description="ソート順序 (desc or asc)"),
    shelf_id: int | None = Query(None, description="特定の棚に所属する本のみを取得"),
    unassigned_only: bool = Query(False, description="棚未登録の本のみを取得"),
    db: Session = Depends(get_db),
):
    logger.info(f"GET /books - limit={limit}, order_by='{order_by}', order='{order}', shelf_id={shelf_id}, unassigned_only={unassigned_only}")

    query = db.query(Book)

    # 棚IDでフィルタリング
    if unassigned_only:
        query = query.filter(Book.shelf_id.is_(None))
    elif shelf_id is not None:
        query = query.filter(Book.shelf_id == shelf_id)

    # ソート処理
    order_column = getattr(Book, order_by, Book.created_at)
    if order.lower() == "desc":
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column.asc())

    # 件数制限
    if limit is not None:
        query = query.limit(limit)

    books = query.all()
    logger.info(f"GET /books - Retrieved {len(books)} books")
    return books


@router.get("/books/{id}", response_model=BookRead)
def read_book(
    id: int,
    db: Session = Depends(get_db),
):
    """
    指定されたIDの書籍を取得
    """
    logger.info(f"GET /books/{id} - Fetching book data")

    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        logger.warning(f"GET /books/{id} - Book not found (404)")
        raise HTTPException(status_code=404, detail="Book not found")

    logger.info(f"GET /books/{id} - Successfully retrieved book data")
    return book


@router.put("/books/{id}", response_model=BookRead)
def update_book(
    id: int,
    book: BookUpdate,
    db: Session = Depends(get_db),
):
    logger.info(f"PUT /books/{id} - Updating book")

    try:
        db_book = db.query(Book).filter(Book.id == id).first()
        if not db_book:
            logger.warning(f"PUT /books/{id} - Book not found (404)")
            raise HTTPException(status_code=404, detail="Book not found")

        # Noneでない値のみを更新
        for key, value in book.model_dump(exclude_unset=True).items():
            if value is not None:
                # BookStatusの場合はvalueに変換
                if isinstance(value, BookStatus):
                    setattr(db_book, key, value.value)
                else:
                    setattr(db_book, key, value)

        db.commit()
        db.refresh(db_book)
        logger.info(f"PUT /books/{id} - Successfully updated book")
        return db_book
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"PUT /books/{id} - Database error: {str(exc)}", exc_info=True)
        raise handle_database_error(exc, "book update") from exc


@router.delete("/books/{id}")
def delete_book(
    id: int,
    db: Session = Depends(get_db),
):
    logger.info(f"DELETE /books/{id} - Deleting book")

    try:
        book = db.query(Book).filter(Book.id == id).first()
        if not book:
            logger.warning(f"DELETE /books/{id} - Book not found (404)")
            raise HTTPException(status_code=404, detail="Book not found")

        db.delete(book)
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
    status: BookStatus = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    """
    書籍のステータスを更新

    status: "unread", "picked", "read" のいずれか
    """
    logger.info(f"PATCH /books/{id}/status - Updating status to '{status.value}'")

    try:
        book = db.query(Book).filter(Book.id == id).first()
        if not book:
            logger.warning(f"PATCH /books/{id}/status - Book not found (404)")
            raise HTTPException(status_code=404, detail="Book not found")

        book.status = status.value
        db.commit()
        db.refresh(book)
        logger.info(f"PATCH /books/{id}/status - Successfully updated status")
        return book
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"PATCH /books/{id}/status - Database error: {str(exc)}", exc_info=True)
        raise handle_database_error(exc, "book status update") from exc
