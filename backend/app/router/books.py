import os

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from sqlalchemy.exc import SQLAlchemyError

from ..database import get_db
from ..models import Book
from ..schemas import BookCreate, BookRead, BookUpdate
from ..exceptions import (
    handle_database_error,
    handle_internal_error,
)

router = APIRouter()


@router.get("/health")
def health():
    return {"message": "OK! The server is running."}


@router.get("/books/random", response_model=list[BookRead])
def random_books(
    db: Session = Depends(get_db),
    include_picked: int = Query(0, description="1でis_picked=1も含める。"),
):
    try:
        pickcount = int(os.getenv("PICKCOUNT", "4"))

        # クエリ実行
        if include_picked == 0:
            query = db.query(Book).filter(Book.is_picked != 1)
        else:
            query = db.query(Book)

        books = query.order_by(func.random()).limit(pickcount).all()
        return books

    except HTTPException:
        raise
    except Exception as exc:
        raise handle_internal_error(exc, "random book selection")


@router.post("/books/", response_model=BookRead)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
):
    try:
        db_book = Book(**book.dict())
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book
    except SQLAlchemyError as exc:
        db.rollback()
        raise handle_database_error(exc, "book creation") from exc


@router.get("/books/", response_model=list[BookRead])
def read_books(
    limit: int | None = Query(None, description="取得件数の上限"),
    order_by: str = Query("created_at", description="ソート対象のフィールド"),
    order: str = Query("desc", description="ソート順序 (desc or asc)"),
    db: Session = Depends(get_db),
):
    query = db.query(Book)

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
    return books


@router.get("/books/{id}", response_model=BookRead)
def read_book(
    id: int,
    db: Session = Depends(get_db),
):
    """
    指定されたIDの書籍を取得
    """
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.put("/books/{id}", response_model=BookRead)
def update_book(
    id: int,
    book: BookUpdate,
    db: Session = Depends(get_db),
):
    try:
        db_book = db.query(Book).filter(Book.id == id).first()
        if not db_book:
            raise HTTPException(status_code=404, detail="Book not found")

        for key, value in book.model_dump().items():
            setattr(db_book, key, value)

        db.commit()
        db.refresh(db_book)
        return db_book
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise handle_database_error(exc, "book update") from exc


@router.delete("/books/{id}")
def delete_book(
    id: int,
    db: Session = Depends(get_db),
):
    try:
        book = db.query(Book).filter(Book.id == id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        db.delete(book)
        db.commit()
        return {"message": "Book deleted successfully"}
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise handle_database_error(exc, "book deletion") from exc


@router.patch("/books/{id}/picked", response_model=BookRead)
def update_book_picked(
    id: int,
    is_picked: int = Body(..., embed=True),  # 1: picked, 0: unpicked
    db: Session = Depends(get_db),
):
    try:
        book = db.query(Book).filter(Book.id == id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        book.is_picked = is_picked
        db.commit()
        db.refresh(book)
        return book
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise handle_database_error(exc, "book picked status update") from exc
