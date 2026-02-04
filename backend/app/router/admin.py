import os
import logging

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from ..database import get_db
from ..models import Book

# .envファイルを読み込み（backend/.env）
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
def health():
    logger.info("GET /health - Health check requested")
    return {"message": "OK! The server is running."}


@router.get("/db-status")
def get_db_status(db: Session = Depends(get_db)):
    """
    データベースの状態情報を取得

    最終更新日時とレコード数を返す。
    """
    logger.info("GET /db-status - Database status requested")

    try:
        # レコード数を取得
        book_count = db.query(Book).count()

        # 最新のレコードの作成日時を取得
        latest_book = db.query(Book).order_by(Book.created_at.desc()).first()

        if latest_book:
            last_modified = latest_book.created_at.isoformat()
        else:
            # レコードがない場合はNoneを返す
            last_modified = None

        logger.info(
            f"GET /db-status - Last modified: {last_modified}, Books: {book_count}"
        )

        return {"last_modified": last_modified, "record_count": book_count}
    except Exception as exc:
        logger.error(
            f"GET /db-status - Error retrieving database status: {str(exc)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Failed to retrieve database status"
        )
