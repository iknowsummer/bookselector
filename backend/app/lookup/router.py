"""
書籍検索エンドポイント

外部APIから書籍情報を検索する
"""

from fastapi import APIRouter, HTTPException

from .schemas import GoogleBooksResponse
from ..exceptions import handle_internal_error
from .google_books import fetch_book_by_isbn
from ..schemas import validate_isbn_format

router = APIRouter()


@router.get("/lookup/isbn/{isbn}", response_model=GoogleBooksResponse)
def lookup_book_by_isbn_endpoint(isbn: str):
    """
    ISBNから書籍情報をGoogle Books APIで検索

    Args:
        isbn: 13桁のISBN

    Returns:
        GoogleBooksResponse: 書籍情報（title, author, description, isbn, image_url）

    Raises:
        HTTPException 400: ISBNフォーマットが不正
        HTTPException 404: 書籍が見つからない
        HTTPException 500: API接続エラー
    """
    # ISBNフォーマット検証（13桁の数字）
    try:
        validate_isbn_format(isbn)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        # Google Books API経由で書籍情報を取得
        book_data = fetch_book_by_isbn(isbn)
        return book_data

    except HTTPException:
        # fetch_book_by_isbnから返されたHTTPExceptionはそのまま伝播
        raise
    except Exception as exc:
        raise handle_internal_error(exc, "ISBN lookup") from exc
