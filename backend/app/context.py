"""User context management for API requests."""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import User


def get_current_user(db: Session = Depends(get_db)) -> User:
    """
    Get current user context.
    Phase 1: Always returns admin user (id=1).
    Future: Will use authentication to determine actual user.

    Returns:
        User: The current user (admin in Phase 1)

    Raises:
        RuntimeError: If admin user doesn't exist
    """
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        raise RuntimeError(
            "Admin user (id=1) not found. "
            "Please run scripts/create_admin_user.py first."
        )
    return user


# Type alias for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
