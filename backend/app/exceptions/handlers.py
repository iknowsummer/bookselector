"""
エラーハンドリング用のヘルパー関数
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from .errors import ERROR_MESSAGES, CommonError


def create_error_response(
    error_code: str, details: str, message: Optional[str] = None
) -> Dict[str, Any]:
    """
    構造化されたエラーレスポンスを作成

    Args:
        error_code: エラーコード
        details: 詳細情報
        message: カスタムメッセージ（Noneの場合はデフォルトメッセージを使用）

    Returns:
        構造化されたエラー辞書
    """
    return {
        "error_code": error_code,
        "message": message or ERROR_MESSAGES.get(error_code, "Unknown error"),
        "details": details,
    }


def handle_database_error(
    exc: SQLAlchemyError, operation: str = "database operation"
) -> HTTPException:
    """
    データベースエラーの統一的な処理

    Args:
        exc: SQLAlchemyError例外
        operation: 実行していた操作の説明

    Returns:
        HTTPException
    """
    error_detail = create_error_response(
        error_code=CommonError.DATABASE_ERROR,
        details=f"Failed during {operation}: {str(exc)}",
    )
    return HTTPException(status_code=500, detail=error_detail)


def handle_validation_error(
    error_code: str, details: str, status_code: int = 400
) -> HTTPException:
    """
    バリデーションエラーの統一的な処理

    Args:
        error_code: エラーコード
        details: 詳細情報
        status_code: HTTPステータスコード

    Returns:
        HTTPException
    """
    error_detail = create_error_response(error_code=error_code, details=details)
    return HTTPException(status_code=status_code, detail=error_detail)


def handle_internal_error(
    exc: Exception, operation: str = "operation"
) -> HTTPException:
    """
    内部エラーの統一的な処理

    Args:
        exc: Exception例外
        operation: 実行していた操作の説明

    Returns:
        HTTPException
    """
    error_detail = create_error_response(
        error_code=CommonError.INTERNAL_ERROR,
        details=f"Unexpected error during {operation}: {str(exc)}",
    )
    return HTTPException(status_code=500, detail=error_detail)
