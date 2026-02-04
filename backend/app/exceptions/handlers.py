"""
エラーハンドリング用のヘルパー関数
"""

from typing import Dict, Any
from fastapi import HTTPException
from .errors import ERROR_MESSAGES, CommonError


def create_error_response(error_code: str, details: str) -> Dict[str, Any]:
    return {
        "error_code": error_code,
        "message": ERROR_MESSAGES.get(error_code, "Unknown error"),
        "details": details,
    }


def handle_database_error(exc, operation: str = "database operation") -> HTTPException:
    error_msg = f"Failed during {operation}: {str(exc)}"
    error_detail = create_error_response(
        error_code=CommonError.DATABASE_ERROR,
        details=error_msg,
    )
    return HTTPException(status_code=500, detail=error_detail)


def handle_internal_error(exc, operation: str = "operation") -> HTTPException:
    error_msg = f"Unexpected error during {operation}: {str(exc)}"
    error_detail = create_error_response(
        error_code=CommonError.INTERNAL_ERROR,
        details=error_msg,
    )
    return HTTPException(status_code=500, detail=error_detail)
