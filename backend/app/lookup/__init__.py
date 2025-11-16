"""
書籍情報検索モジュール

外部API（Google Books API等）から書籍情報を取得する
"""
from .google_books import fetch_book_by_isbn

__all__ = ["fetch_book_by_isbn"]
