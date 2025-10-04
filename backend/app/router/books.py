import os
from datetime import datetime

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from sqlalchemy.exc import SQLAlchemyError

from database import get_db
from models import Book, Result
from schemas import BookCreate, BookRead, ResultCreate, ResultRead
from exceptions import (
    handle_database_error,
    handle_internal_error,
)

router = APIRouter()


@router.get("/health")
def health():
    return {"message": "Hello, FastAPI!"}


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
def read_books(id: list[int] = Query(None), db: Session = Depends(get_db)):
    if id is not None:
        books = db.query(Book).filter(Book.id.in_(id)).all()
    else:
        books = db.query(Book).all()
    return books


@router.patch("/books/picked", response_model=list[BookRead])
def update_books_picked(
    ids: list[int] = Body(...),
    is_picked: int = Body(..., embed=True),  # 1: picked, 0: unpicked
    db: Session = Depends(get_db),
):
    books = db.query(Book).filter(Book.id.in_(ids)).all()
    for book in books:
        book.is_picked = is_picked
    db.commit()
    return books


@router.post("/results/", response_model=ResultRead)
def create_result(
    result: ResultCreate,
    db: Session = Depends(get_db),
):
    try:
        db_result = Result(
            book_ids=result.book_ids,
            note=result.note,
            created_at=datetime.now().isoformat(),
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        return db_result
    except SQLAlchemyError as exc:
        db.rollback()
        raise handle_database_error(exc, "result creation") from exc


@router.get("/results/", response_model=list[ResultRead])
def read_results(db: Session = Depends(get_db)):
    try:
        return db.query(Result).all()
    except SQLAlchemyError as exc:
        raise handle_database_error(exc, "results retrieval") from exc
