from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from database import Base, engine, SessionLocal
from models import Book
import os
from dotenv import load_dotenv


load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
app = FastAPI()


# 初回起動時にDBテーブルを自動作成
Base.metadata.create_all(bind=engine)


# DBセッションをリクエストごとに管理
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Hello, FastAPI!"}


# ランダムで指定数の書籍を取得するエンドポイント
@app.get("/books/pick/")
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


@app.post("/books/")
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


@app.get("/books/")
def read_books(db: Session = Depends(get_db)):
    return db.query(Book).all()
