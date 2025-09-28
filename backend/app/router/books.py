import os
from datetime import datetime

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from sqlalchemy.exc import SQLAlchemyError

from database import get_db
from models import Book, Result
from schemas import BookCreate, BookRead, ResultCreate, ResultRead
from exceptions import (
    BookError,
    ResultError,
    handle_database_error,
    handle_validation_error,
    handle_internal_error,
)

router = APIRouter()


@router.get("/")
def root():
    return {"message": "Hello, FastAPI!"}


@router.get("/books/random", response_model=list[BookRead])
def random_books(
    db: Session = Depends(get_db),
    include_picked: int = Query(0, description="1でis_picked=1も含める。"),
):
    try:
        # 環境変数の取得とバリデーション
        pickcount_str = os.getenv("PICKCOUNT", "4")
        try:
            pickcount = int(pickcount_str)
            if pickcount <= 0:
                raise ValueError("PICKCOUNT must be positive")
        except ValueError:
            raise handle_validation_error(
                error_code=BookError.INVALID_CONFIG,
                details=f"PICKCOUNT must be a positive integer, got: {pickcount_str}",
                status_code=500,
            )

        # include_pickedのバリデーション
        if include_picked not in [0, 1]:
            raise handle_validation_error(
                error_code=BookError.INVALID_PARAMETER,
                details=f"include_picked must be 0 or 1, got: {include_picked}",
            )

        # クエリ実行
        if include_picked == 0:
            query = db.query(Book).filter(Book.is_picked != 1)
        else:
            query = db.query(Book)

        books = query.order_by(func.random()).limit(pickcount).all()
        return books

    except HTTPException:
        raise
    except Exception as e:
        raise handle_internal_error(e, "random book selection")


@router.post("/books/", response_model=BookRead)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
):
    try:
        db_book = Book(**book.dict())
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book
    except SQLAlchemyError as exc:
        db.rollback()
        raise handle_database_error(exc, "book creation") from exc
    except Exception as exc:
        db.rollback()
        raise handle_internal_error(exc, "book creation") from exc


@router.get("/books/", response_model=list[BookRead])
def read_books(id: list[int] = Query(None), db: Session = Depends(get_db)):
    try:
        # IDリストのバリデーション
        if id is not None:
            if not id:  # 空リストの場合
                raise handle_validation_error(
                    error_code=BookError.EMPTY_ID_LIST,
                    details="Please provide at least one book ID",
                )
            if any(book_id <= 0 for book_id in id):
                invalid_ids = [book_id for book_id in id if book_id <= 0]
                raise handle_validation_error(
                    error_code=BookError.INVALID_ID,
                    details=f"All IDs must be positive integers, invalid IDs: {invalid_ids}",
                )
            books = db.query(Book).filter(Book.id.in_(id)).all()
        else:
            books = db.query(Book).all()
        return books
    except HTTPException:
        raise
    except Exception as e:
        raise handle_internal_error(e, "book retrieval")


@router.patch("/books/picked", response_model=list[BookRead])
def update_books_picked(
    ids: list[int] = Body(...),
    is_picked: int = Body(..., embed=True),  # 1: picked, 0: unpicked
    db: Session = Depends(get_db),
):
    try:
        # 入力値のバリデーション
        if not ids:
            raise handle_validation_error(
                error_code=BookError.EMPTY_ID_LIST,
                details="Please provide at least one book ID",
            )
        if any(book_id <= 0 for book_id in ids):
            invalid_ids = [book_id for book_id in ids if book_id <= 0]
            raise handle_validation_error(
                error_code=BookError.INVALID_ID,
                details=f"All IDs must be positive integers, invalid IDs: {invalid_ids}",
            )
        if is_picked not in [0, 1]:
            raise handle_validation_error(
                error_code=BookError.INVALID_PARAMETER,
                details=f"is_picked must be 0 or 1, got: {is_picked}",
            )

        books = db.query(Book).filter(Book.id.in_(ids)).all()
        if not books:
            raise handle_validation_error(
                error_code=BookError.BOOKS_NOT_FOUND,
                details=f"No books found with IDs: {ids}",
                status_code=404,
            )

        # 部分的に見つからないIDがある場合の警告
        found_ids = {book.id for book in books}
        missing_ids = set(ids) - found_ids
        if missing_ids:
            raise handle_validation_error(
                error_code=BookError.PARTIAL_BOOKS_NOT_FOUND,
                details=f"Books with IDs {list(missing_ids)} not found",
                status_code=404,
            )

        for book in books:
            book.is_picked = is_picked
        db.commit()
        return books

    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise handle_database_error(exc, "book picked status update") from exc
    except Exception as exc:
        db.rollback()
        raise handle_internal_error(exc, "book picked status update") from exc


@router.post("/results/", response_model=ResultRead)
def create_result(
    result: ResultCreate,
    db: Session = Depends(get_db),
):
    try:
        # 入力値のバリデーション
        if not result.book_ids:
            raise handle_validation_error(
                error_code=ResultError.EMPTY_BOOK_IDS,
                details="Please provide at least one book ID",
            )

        db_result = Result(
            book_ids=result.book_ids,
            note=result.note,
            created_at=datetime.now().isoformat(),
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        return db_result
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise handle_database_error(exc, "result creation") from exc
    except Exception as exc:
        db.rollback()
        raise handle_internal_error(exc, "result creation") from exc


@router.get("/results/", response_model=list[ResultRead])
def read_results(db: Session = Depends(get_db)):
    try:
        return db.query(Result).all()
    except SQLAlchemyError as exc:
        raise handle_database_error(exc, "results retrieval") from exc
    except Exception as exc:
        raise handle_internal_error(exc, "results retrieval") from exc
