import os
from datetime import datetime

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from ..database import get_db
from ..models import Book, Result
from ..schemas import BookCreate, BookRead, ResultCreate, ResultRead

router = APIRouter()


@router.get("/")
def root():
    return {"message": "Hello, FastAPI!"}


@router.get("/books/random", response_model=list[BookRead])
def random_books(
    db: Session = Depends(get_db),
    include_picked: int = Query(0, description="1でis_picked=1も含める。"),
):
    pickcount = int(os.getenv("PICKCOUNT", "4"))
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
    try:
        db.commit()
        db.refresh(db_book)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="書籍の登録中にエラーが発生しました。") from exc
    return db_book


@router.get("/books/", response_model=list[BookRead])
def read_books(id: list[int] = Query(None), db: Session = Depends(get_db)):
    if id:
        books = db.query(Book).filter(Book.id.in_(id)).all()
    else:
        books = db.query(Book).all()
    return books


@router.patch("/books/picked", response_model=list[BookRead])
def update_books_picked(
    ids: list[int] = Body(...),
    is_picked: int = Body(..., embed=True),  # 1: 選出済み、0: 未選出
    db: Session = Depends(get_db),
):
    books = db.query(Book).filter(Book.id.in_(ids)).all()
    if not books:
        raise HTTPException(status_code=404, detail="指定した書籍が見つかりません。")
    for book in books:
        book.is_picked = is_picked
    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="書籍の更新中にエラーが発生しました。") from exc
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
    try:
        db.commit()
        db.refresh(db_result)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="結果の登録中にエラーが発生しました。") from exc
    return db_result


@router.get("/results/", response_model=list[ResultRead])
def read_results(db: Session = Depends(get_db)):
    return db.query(Result).all()
