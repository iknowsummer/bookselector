from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# 相対インポートに統一
from .database import Base, engine
import os

from dotenv import load_dotenv

from .router import books_router

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 初回起動時にDBテーブルを自動作成
Base.metadata.create_all(bind=engine)

# ルーターを登録
app.include_router(books_router)
