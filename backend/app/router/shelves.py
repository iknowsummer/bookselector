import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..context import CurrentUser
from ..database import get_db
from ..models import Shelf
from ..schemas import ShelfCreate, ShelfRead, ShelfUpdate
from ..exceptions import handle_database_error, handle_internal_error

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/shelves/", response_model=list[ShelfRead])
def read_shelves(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """棚一覧を取得 (user-scoped)"""
    logger.info("GET /shelves - Fetching shelf list for user_id=%s", current_user.id)
    shelves = db.query(Shelf).filter(
        Shelf.user_id == current_user.id
    ).order_by(Shelf.id.asc()).all()
    logger.info("GET /shelves - Retrieved %s shelves for user_id=%s", len(shelves), current_user.id)
    return shelves


@router.get("/shelves/{shelf_id}", response_model=ShelfRead)
def read_shelf(
    shelf_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """棚詳細を取得 (user-scoped)"""
    logger.info("GET /shelves/%s - Fetching shelf detail for user_id=%s", shelf_id, current_user.id)
    shelf = db.query(Shelf).filter(
        Shelf.id == shelf_id,
        Shelf.user_id == current_user.id
    ).first()
    if not shelf:
        logger.warning("GET /shelves/%s - Shelf not found for user_id=%s", shelf_id, current_user.id)
        raise HTTPException(status_code=404, detail="Shelf not found")
    return shelf


@router.post("/shelves/", response_model=ShelfRead)
def create_shelf(
    shelf: ShelfCreate,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """棚を新規作成 (user-scoped)"""
    logger.info("POST /shelves - Creating shelf: name='%s' for user_id=%s", shelf.name, current_user.id)
    try:
        db_shelf = Shelf(**shelf.model_dump(), user_id=current_user.id)
        db.add(db_shelf)
        db.commit()
        db.refresh(db_shelf)
        logger.info("POST /shelves - Created shelf id=%s for user_id=%s", db_shelf.id, current_user.id)
        return db_shelf
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("POST /shelves - Database error: %s", exc, exc_info=True)
        raise handle_database_error(exc, "shelf creation") from exc
    except Exception as exc:  # 念のため予期しない例外を補足
        db.rollback()
        logger.error("POST /shelves - Unexpected error: %s", exc, exc_info=True)
        raise handle_internal_error(exc, "shelf creation") from exc


@router.put("/shelves/{shelf_id}", response_model=ShelfRead)
def update_shelf(
    shelf_id: int,
    shelf: ShelfUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """棚情報を更新 (user-scoped)"""
    logger.info("PUT /shelves/%s - Updating shelf for user_id=%s", shelf_id, current_user.id)
    try:
        db_shelf = db.query(Shelf).filter(
            Shelf.id == shelf_id,
            Shelf.user_id == current_user.id
        ).first()
        if not db_shelf:
            logger.warning("PUT /shelves/%s - Shelf not found for user_id=%s", shelf_id, current_user.id)
            raise HTTPException(status_code=404, detail="Shelf not found")

        for key, value in shelf.model_dump(exclude_unset=True).items():
            setattr(db_shelf, key, value)

        db.commit()
        db.refresh(db_shelf)
        logger.info("PUT /shelves/%s - Updated shelf for user_id=%s", shelf_id, current_user.id)
        return db_shelf
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("PUT /shelves/%s - Database error: %s", shelf_id, exc, exc_info=True)
        raise handle_database_error(exc, "shelf update") from exc


@router.delete("/shelves/{shelf_id}")
def delete_shelf(
    shelf_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """棚を削除 (user-scoped)"""
    logger.info("DELETE /shelves/%s - Deleting shelf for user_id=%s", shelf_id, current_user.id)
    try:
        shelf = db.query(Shelf).filter(
            Shelf.id == shelf_id,
            Shelf.user_id == current_user.id
        ).first()
        if not shelf:
            logger.warning("DELETE /shelves/%s - Shelf not found for user_id=%s", shelf_id, current_user.id)
            raise HTTPException(status_code=404, detail="Shelf not found")

        db.delete(shelf)
        db.commit()
        logger.info("DELETE /shelves/%s - Deleted shelf for user_id=%s", shelf_id, current_user.id)
        return {"message": "Shelf deleted successfully"}
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("DELETE /shelves/%s - Database error: %s", shelf_id, exc, exc_info=True)
        raise handle_database_error(exc, "shelf deletion") from exc
