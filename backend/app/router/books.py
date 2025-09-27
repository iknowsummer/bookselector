import os
from datetime import datetime

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from database import get_db
from models import Book, Result
from schemas import BookCreate, BookRead, ResultCreate, ResultRead

router = APIRouter()


@router.get("/")
def root():
    return {"message": "Hello, FastAPI!"}


@router.get("/books/pick/", response_model=list[BookRead])
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


@router.post("/books/", response_model=BookRead)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
):
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@router.get("/books/", response_model=list[BookRead])
def read_books(db: Session = Depends(get_db)):
    return db.query(Book).all()


@router.get("/books/ids/", response_model=list[BookRead])
def get_books_by_ids(id: list[int] = Query(...), db: Session = Depends(get_db)):
    books = db.query(Book).filter(Book.id.in_(id)).all()
    return books


@router.post("/books/picked", response_model=list[BookRead])
def update_is_picked(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    books = db.query(Book).filter(Book.id.in_(ids)).all()
    if not books:
        raise HTTPException(status_code=404, detail="Books not found")
    for book in books:
        book.is_picked = 1
    db.commit()
    return books


@router.post("/books/unpicked", response_model=list[BookRead])
def unpick_book(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    books = db.query(Book).filter(Book.id.in_(ids)).all()
    if not books:
        raise HTTPException(status_code=404, detail="Books not found")
    for book in books:
        book.is_picked = 0
    db.commit()
    return books


@router.post("/results/", response_model=ResultRead)
def create_result(
    result: ResultCreate,
    db: Session = Depends(get_db),
):
    db_result = Result(
        book_ids=result.book_ids,
        note=result.note,
        created_at=datetime.now().isoformat(),
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result


@router.get("/results/", response_model=list[ResultRead])
def read_results(db: Session = Depends(get_db)):
    return db.query(Result).all()
