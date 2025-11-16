"""
書籍検索APIのレスポンススキーマ
"""
from pydantic import BaseModel


class GoogleBooksResponse(BaseModel):
    """
    Google Books APIから取得した書籍情報

    注意: target_age と note は含まない（Google Books APIでは取得できないため）
    """

    title: str
    author: str | None = None
    description: str | None = None
    isbn: str
    image_url: str | None = None
