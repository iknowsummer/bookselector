"""
エラーコードと関連メッセージの定義
"""


class CommonError:
    DATABASE_ERROR = "DATABASE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


ERROR_MESSAGES = {
    CommonError.DATABASE_ERROR: "Database error occurred",
    CommonError.INTERNAL_ERROR: "Internal server error",
}
