"""
Google Books API連携モジュール

ISBNから書籍情報を取得してGoogleBooksResponseスキーマに変換する
"""
import logging
import requests
from fastapi import HTTPException

from .schemas import GoogleBooksResponse

logger = logging.getLogger(__name__)


def fetch_book_by_isbn(isbn: str) -> GoogleBooksResponse:
    """
    ISBNから書籍情報をGoogle Books APIで検索してGoogleBooksResponseスキーマに変換

    Args:
        isbn: 13桁のISBN（バリデーション済み前提）

    Returns:
        GoogleBooksResponse: 書籍情報（title, author, description, isbn, image_url）

    Raises:
        HTTPException 404: 書籍が見つからない
        HTTPException 500: API接続エラー
    """
    logger.info(f"Fetching book info from Google Books API - ISBN: {isbn}")

    try:
        # Google Books APIにリクエスト
        url = "https://www.googleapis.com/books/v1/volumes"
        params = {
            "q": f"isbn:{isbn}",
            "maxResults": 1,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        items = data.get("items", [])

        if not items:
            logger.warning(f"No book found for ISBN: {isbn}")
            raise HTTPException(
                status_code=404,
                detail=f"Book not found for ISBN: {isbn}"
            )

        # 最初の書籍情報を取得
        volume_info = items[0].get("volumeInfo", {})

        # 書籍情報を抽出
        title = volume_info.get("title", "")
        authors = volume_info.get("authors", [])
        author = ", ".join(authors) if authors else None
        description = volume_info.get("description")

        # 画像URLを取得（大きい画像を優先）
        image_url = None
        if "imageLinks" in volume_info:
            img = volume_info["imageLinks"]
            for key in ["extraLarge", "large", "medium", "small", "thumbnail", "smallThumbnail"]:
                if key in img:
                    image_url = img[key]
                    break

        # GoogleBooksResponseスキーマに変換
        book_data = GoogleBooksResponse(
            title=title,
            author=author,
            description=description,
            isbn=isbn,
            image_url=image_url,
        )

        logger.info(f"Successfully fetched book info for ISBN: {isbn}")
        return book_data

    except HTTPException:
        raise
    except requests.exceptions.RequestException as exc:
        logger.error(f"Google Books API error for ISBN {isbn}: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Google Books APIへの接続に失敗しました"
        ) from exc
    except Exception as exc:
        logger.error(f"Unexpected error while fetching book for ISBN {isbn}: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="書籍情報の取得中に予期しないエラーが発生しました"
        ) from exc
