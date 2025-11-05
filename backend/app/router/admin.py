import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
def health():
    logger.info("GET /health - Health check requested")
    return {"message": "OK! The server is running."}
