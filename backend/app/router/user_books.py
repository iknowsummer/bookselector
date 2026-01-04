from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..context import CurrentUser
from ..database import get_db
from ..schemas import UserBookCreate, UserBookRead, UserBookUpdate
from ..services.user_books import (
    create_user_book as create_user_book_service,
    update_user_book as update_user_book_service,
    delete_user_book as delete_user_book_service,
)

router = APIRouter()


@router.post("/user-books/", response_model=UserBookRead)
def create_user_book(
    payload: UserBookCreate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    return create_user_book_service(payload, current_user.id, db)


@router.put("/user-books/{book_id}", response_model=UserBookRead)
def update_user_book(
    book_id: int,
    payload: UserBookUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    return update_user_book_service(book_id, payload, current_user.id, db)


@router.delete("/user-books/{book_id}")
def delete_user_book(
    book_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    return delete_user_book_service(book_id, current_user.id, db)
