from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import Book

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
