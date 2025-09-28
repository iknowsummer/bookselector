"""
エラーコードと関連メッセージの定義
"""


class BookError:
    """書籍関連のエラーコード"""

    BOOKS_NOT_FOUND = "BOOKS_NOT_FOUND"
    PARTIAL_BOOKS_NOT_FOUND = "PARTIAL_BOOKS_NOT_FOUND"
    EMPTY_ID_LIST = "EMPTY_ID_LIST"
    INVALID_ID = "INVALID_ID"
    INVALID_PARAMETER = "INVALID_PARAMETER"
    INVALID_CONFIG = "INVALID_CONFIG"


class ResultError:
    """結果関連のエラーコード"""

    EMPTY_BOOK_IDS = "EMPTY_BOOK_IDS"


class CommonError:
    """共通エラーコード"""

    DATABASE_ERROR = "DATABASE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# エラーコードと基本メッセージのマッピング
ERROR_MESSAGES = {
    # Book関連
    BookError.BOOKS_NOT_FOUND: "Books not found",
    BookError.PARTIAL_BOOKS_NOT_FOUND: "Some books not found",
    BookError.EMPTY_ID_LIST: "ID list cannot be empty",
    BookError.INVALID_ID: "Invalid book IDs",
    BookError.INVALID_PARAMETER: "Invalid parameter",
    BookError.INVALID_CONFIG: "Invalid configuration",
    # Result関連
    ResultError.EMPTY_BOOK_IDS: "Book IDs cannot be empty",
    # 共通
    CommonError.DATABASE_ERROR: "Database error occurred",
    CommonError.INTERNAL_ERROR: "Internal server error",
}
