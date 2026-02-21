from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..context import CurrentUser
from ..database import get_db
from ..models import Shelf
from ..schemas import ShelfCreate, ShelfRead, ShelfUpdate
from ..exceptions import handle_database_error, handle_internal_error

router = APIRouter()


@router.get("/shelves", response_model=list[ShelfRead])
def read_shelves(current_user: CurrentUser, db: Session = Depends(get_db)):
    """棚一覧を取得 (user-scoped)"""
    shelves = (
        db.query(Shelf)
        .filter(Shelf.user_id == current_user.id)
        .order_by(Shelf.id.asc())
        .all()
    )
    return shelves


@router.get("/shelves/{shelf_id}", response_model=ShelfRead)
def read_shelf(shelf_id: int, current_user: CurrentUser, db: Session = Depends(get_db)):
    """棚詳細を取得 (user-scoped)"""
    shelf = (
        db.query(Shelf)
        .filter(Shelf.id == shelf_id, Shelf.user_id == current_user.id)
        .first()
    )
    if not shelf:
        raise HTTPException(status_code=404, detail="Shelf not found")
    return shelf


@router.post("/shelves", response_model=ShelfRead)
def create_shelf(
    shelf: ShelfCreate, current_user: CurrentUser, db: Session = Depends(get_db)
):
    """棚を新規作成 (user-scoped)"""
    try:
        db_shelf = Shelf(**shelf.model_dump(), user_id=current_user.id)
        db.add(db_shelf)
        db.commit()
        db.refresh(db_shelf)
        return db_shelf
    except SQLAlchemyError as exc:
        db.rollback()
        raise handle_database_error(exc, "shelf creation") from exc
    except Exception as exc:
        db.rollback()
        raise handle_internal_error(exc, "shelf creation") from exc


@router.put("/shelves/{shelf_id}", response_model=ShelfRead)
def update_shelf(
    shelf_id: int,
    shelf: ShelfUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """棚情報を更新 (user-scoped)"""
    try:
        db_shelf = (
            db.query(Shelf)
            .filter(Shelf.id == shelf_id, Shelf.user_id == current_user.id)
            .first()
        )
        if not db_shelf:
            raise HTTPException(status_code=404, detail="Shelf not found")

        for key, value in shelf.model_dump(exclude_unset=True).items():
            setattr(db_shelf, key, value)

        db.commit()
        db.refresh(db_shelf)
        return db_shelf
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise handle_database_error(exc, "shelf update") from exc


@router.delete("/shelves/{shelf_id}")
def delete_shelf(
    shelf_id: int, current_user: CurrentUser, db: Session = Depends(get_db)
):
    """棚を削除 (user-scoped)"""
    try:
        shelf = (
            db.query(Shelf)
            .filter(Shelf.id == shelf_id, Shelf.user_id == current_user.id)
            .first()
        )
        if not shelf:
            raise HTTPException(status_code=404, detail="Shelf not found")

        db.delete(shelf)
        db.commit()
        return {"message": "Shelf deleted successfully"}
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise handle_database_error(exc, "shelf deletion") from exc
