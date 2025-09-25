import os

from dotenv import load_dotenv
from fastapi import FastAPI

from database import Base, engine
from router import books_router

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI()

# 初回起動時にDBテーブルを自動作成
Base.metadata.create_all(bind=engine)

# ルーターを登録
app.include_router(books_router)
