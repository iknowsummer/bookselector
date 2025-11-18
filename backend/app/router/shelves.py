import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Shelf
from ..schemas import ShelfCreate, ShelfRead, ShelfUpdate
from ..exceptions import handle_database_error, handle_internal_error

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/shelves/", response_model=list[ShelfRead])
def read_shelves(db: Session = Depends(get_db)):
    """棚一覧を取得"""
    logger.info("GET /shelves - Fetching shelf list")
    shelves = db.query(Shelf).order_by(Shelf.id.asc()).all()
    logger.info("GET /shelves - Retrieved %s shelves", len(shelves))
    return shelves


@router.get("/shelves/{shelf_id}", response_model=ShelfRead)
def read_shelf(shelf_id: int, db: Session = Depends(get_db)):
    """棚詳細を取得"""
    logger.info("GET /shelves/%s - Fetching shelf detail", shelf_id)
    shelf = db.query(Shelf).filter(Shelf.id == shelf_id).first()
    if not shelf:
        logger.warning("GET /shelves/%s - Shelf not found", shelf_id)
        raise HTTPException(status_code=404, detail="Shelf not found")
    return shelf


@router.post("/shelves/", response_model=ShelfRead)
def create_shelf(shelf: ShelfCreate, db: Session = Depends(get_db)):
    """棚を新規作成"""
    logger.info("POST /shelves - Creating shelf: name='%s'", shelf.name)
    try:
        db_shelf = Shelf(**shelf.model_dump())
        db.add(db_shelf)
        db.commit()
        db.refresh(db_shelf)
        logger.info("POST /shelves - Created shelf id=%s", db_shelf.id)
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
def update_shelf(shelf_id: int, shelf: ShelfUpdate, db: Session = Depends(get_db)):
    """棚情報を更新"""
    logger.info("PUT /shelves/%s - Updating shelf", shelf_id)
    try:
        db_shelf = db.query(Shelf).filter(Shelf.id == shelf_id).first()
        if not db_shelf:
            logger.warning("PUT /shelves/%s - Shelf not found", shelf_id)
            raise HTTPException(status_code=404, detail="Shelf not found")

        for key, value in shelf.model_dump(exclude_unset=True).items():
            setattr(db_shelf, key, value)

        db.commit()
        db.refresh(db_shelf)
        logger.info("PUT /shelves/%s - Updated shelf", shelf_id)
        return db_shelf
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("PUT /shelves/%s - Database error: %s", shelf_id, exc, exc_info=True)
        raise handle_database_error(exc, "shelf update") from exc


@router.delete("/shelves/{shelf_id}")
def delete_shelf(shelf_id: int, db: Session = Depends(get_db)):
    """棚を削除"""
    logger.info("DELETE /shelves/%s - Deleting shelf", shelf_id)
    try:
        shelf = db.query(Shelf).filter(Shelf.id == shelf_id).first()
        if not shelf:
            logger.warning("DELETE /shelves/%s - Shelf not found", shelf_id)
            raise HTTPException(status_code=404, detail="Shelf not found")

        db.delete(shelf)
        db.commit()
        logger.info("DELETE /shelves/%s - Deleted shelf", shelf_id)
        return {"message": "Shelf deleted successfully"}
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("DELETE /shelves/%s - Database error: %s", shelf_id, exc, exc_info=True)
        raise handle_database_error(exc, "shelf deletion") from exc
