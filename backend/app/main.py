from fastapi import FastAPI, Depends, Query, HTTPException, Body
from fastapi.responses import HTMLResponse
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from database import Base, engine, SessionLocal
from models import Book, Result
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


@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <!DOCTYPE html>
    <html lang="ja">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Book Selector</title>
        <style>
          body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            margin: 0;
            padding: 32px;
            background-color: #f5f5f5;
            color: #333;
          }
          h1 {
            margin-bottom: 16px;
            font-size: 28px;
            text-align: center;
          }
          p.description {
            margin: 0 auto 24px;
            max-width: 640px;
            line-height: 1.6;
            text-align: center;
          }
          button {
            display: block;
            margin: 0 auto 24px;
            padding: 12px 24px;
            font-size: 16px;
            border: none;
            border-radius: 9999px;
            background: linear-gradient(135deg, #4f46e5, #22d3ee);
            color: white;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
          }
          button:hover:not([disabled]) {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(79, 70, 229, 0.3);
          }
          button:active:not([disabled]) {
            transform: translateY(0);
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
          }
          button[disabled] {
            cursor: not-allowed;
            opacity: 0.6;
            box-shadow: none;
          }
          #results {
            max-width: 720px;
            margin: 0 auto;
            display: grid;
            gap: 16px;
          }
          .card {
            padding: 20px;
            border-radius: 16px;
            background-color: white;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
          }
          .card h2 {
            margin: 0 0 8px;
            font-size: 20px;
          }
          .card p {
            margin: 4px 0;
            line-height: 1.5;
          }
          .empty {
            text-align: center;
            color: #666;
          }
          .error {
            text-align: center;
            color: #b91c1c;
          }
        </style>
      </head>
      <body>
        <h1>Book Selector</h1>
        <p class="description">バックエンドのランダム書籍取得エンドポイントを呼び出し、選ばれた書籍情報を表示します。</p>
        <button id="fetchButton">ランダムな書籍を取得する</button>
        <div id="status" class="empty">ボタンを押して書籍を取得してください。</div>
        <div id="results"></div>
        <script>
          // 書籍カードを描画する関数
          const renderBooks = (books) => {
            const resultsContainer = document.getElementById("results");
            resultsContainer.innerHTML = "";

            if (!books.length) {
              document.getElementById("status").textContent = "書籍情報が見つかりませんでした。";
              document.getElementById("status").className = "empty";
              return;
            }

            document.getElementById("status").textContent = "";
            document.getElementById("status").className = "";

            books.forEach((book) => {
              const card = document.createElement("article");
              card.className = "card";

              const title = document.createElement("h2");
              title.textContent = book.title ?? "タイトル不明";

              const author = document.createElement("p");
              author.innerHTML = `<strong>著者:</strong> ${book.author ?? "不明"}`;

              const description = document.createElement("p");
              description.innerHTML = `<strong>説明:</strong> ${book.description ?? "記載なし"}`;

              const note = document.createElement("p");
              note.innerHTML = `<strong>メモ:</strong> ${book.note ?? "記載なし"}`;

              card.appendChild(title);
              card.appendChild(author);
              card.appendChild(description);
              card.appendChild(note);
              resultsContainer.appendChild(card);
            });
          };

          // エラー表示を行う関数
          const showError = (message) => {
            const status = document.getElementById("status");
            status.textContent = message;
            status.className = "error";
            document.getElementById("results").innerHTML = "";
          };

          // ボタン押下でAPIを呼び出す処理
          document.getElementById("fetchButton").addEventListener("click", async () => {
            const button = document.getElementById("fetchButton");
            button.disabled = true;
            button.textContent = "取得中...";
            const status = document.getElementById("status");
            status.textContent = "書籍情報を取得しています...";
            status.className = "empty";

            try {
              const response = await fetch("/books/pick/");

              if (!response.ok) {
                throw new Error("レスポンスが不正です");
              }

              const books = await response.json();
              renderBooks(Array.isArray(books) ? books : []);
            } catch (error) {
              console.error("API呼び出しでエラーが発生しました", error);
              showError("書籍情報の取得に失敗しました。時間をおいて再度お試しください。");
            } finally {
              button.disabled = false;
              button.textContent = "ランダムな書籍を取得する";
            }
          });
        </script>
      </body>
    </html>
    """


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


@app.get("/books/ids/")
def get_books_by_ids(id: List[int] = Query(...), db: Session = Depends(get_db)):
    books = db.query(Book).filter(Book.id.in_(id)).all()
    return books


# 配列指定のid書籍のis_pickedを1にするエンドポイント
@app.post("/books/picked")
def update_is_picked(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    books = db.query(Book).filter(Book.id.in_(ids)).all()
    if not books:
        raise HTTPException(status_code=404, detail="Books not found")
    for book in books:
        book.is_picked = 1
    db.commit()
    return books


# 配列指定の書籍のis_pickedをNULLにするエンドポイント
@app.post("/books/unpicked")
def unpick_book(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    books = db.query(Book).filter(Book.id.in_(ids)).all()
    if not books:
        raise HTTPException(status_code=404, detail="Books not found")
    for book in books:
        book.is_picked = None
    db.commit()
    db.refresh(book)
    return book


# 結果を登録するエンドポイント
@app.post("/results/")
def create_result(
    book_ids: list[int] = Body(...),
    note: str = None,
    db: Session = Depends(get_db),
):
    from datetime import datetime
    import json

    created_at = datetime.now().isoformat()
    result = Result(book_ids=json.dumps(book_ids), note=note, created_at=created_at)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


# 結果を取得するエンドポイント
@app.get("/results/")
def read_results(db: Session = Depends(get_db)):
    return db.query(Result).all()
