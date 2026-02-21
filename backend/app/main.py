import os
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .database import Base, engine
from .middleware import AccessLogMiddleware
from .logging_config import setup_logging
from .router import (
    books_router,
    admin_router,
    shelves_router,
    user_books_router,
    lookup_router,
)

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# ロギング設定（コンソール + ファイル出力）
log_dir = Path(__file__).parent.parent / "logs"
setup_logging(log_dir=str(log_dir))

logger = logging.getLogger(__name__)

enable_docs = os.getenv("ENABLE_DOCS", "").strip().lower() in ("1", "true")
app = FastAPI(
    docs_url="/docs" if enable_docs else None,
    redoc_url="/redoc" if enable_docs else None,
    openapi_url="/openapi.json" if enable_docs else None,
)

# アクセスログミドルウェア（最初に登録 = 最後に実行）
app.add_middleware(AccessLogMiddleware)

# CORS設定
cors_origins_raw = os.getenv("BACKEND_CORS_ORIGINS", "")
cors_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]

if not cors_origins:
    logger.warning("BACKEND_CORS_ORIGINS が未設定です。CORSリクエストはすべて拒否されます。")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 初回起動時にDBテーブルを自動作成
Base.metadata.create_all(bind=engine)

# ルーターを登録
app.include_router(admin_router)
app.include_router(books_router)
app.include_router(shelves_router)
app.include_router(user_books_router)
app.include_router(lookup_router)
