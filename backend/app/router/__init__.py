from .books import router as books_router
from .admin import router as admin_router
from .shelves import router as shelves_router
from ..lookup.router import router as lookup_router

__all__ = ["books_router", "admin_router", "shelves_router", "lookup_router"]
