import json
import os
from collections.abc import Generator
from datetime import datetime
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from database import SessionLocal
from models import Book, Result

router = APIRouter()


def get_db() -> Generator[Session, None, None]:
    """リクエストごとにSQLAlchemyセッションを管理する依存関係"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def root():
    return {"message": "Hello, FastAPI!"}


@router.get("/books/pick/")
def pick_books(
    db: Session = Depends(get_db),
    include_picked: int = Query(0, description="1でis_picked=1も含める。"),
):
    pickcount = int(os.getenv("PICKCOUNT", 4))

    if include_picked == 0:
        query = db.query(Book).filter(Book.is_picked != 1)
    else:
        query = db.query(Book)

    books = query.order_by(func.random()).limit(pickcount).all()
    return books


@router.post("/books/")
def create_book(
    title: str,
    author: str,
    description: str = None,
    note: str = None,
    db: Session = Depends(get_db),
):
    book = Book(title=title, author=author, description=description, note=note)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.get("/books/")
def read_books(db: Session = Depends(get_db)):
    return db.query(Book).all()


@router.get("/books/ids/")
def get_books_by_ids(id: List[int] = Query(...), db: Session = Depends(get_db)):
    books = db.query(Book).filter(Book.id.in_(id)).all()
    return books


@router.post("/books/picked")
def update_is_picked(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    books = db.query(Book).filter(Book.id.in_(ids)).all()
    if not books:
        raise HTTPException(status_code=404, detail="Books not found")
    for book in books:
        book.is_picked = 1
    db.commit()
    return books


@router.post("/books/unpicked")
def unpick_book(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    books = db.query(Book).filter(Book.id.in_(ids)).all()
    if not books:
        raise HTTPException(status_code=404, detail="Books not found")
    for book in books:
        book.is_picked = None
    db.commit()
    db.refresh(book)
    return book


@router.post("/results/")
def create_result(
    book_ids: list[int] = Body(...),
    note: str = None,
    db: Session = Depends(get_db),
):
    created_at = datetime.now().isoformat()
    result = Result(book_ids=json.dumps(book_ids), note=note, created_at=created_at)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


@router.get("/results/")
def read_results(db: Session = Depends(get_db)):
    return db.query(Result).all()
