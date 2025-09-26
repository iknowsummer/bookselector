from pydantic import BaseModel
from typing import Optional, List


class BookBase(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
    age: Optional[str] = None
    isbn: Optional[str] = None
    image_url: Optional[str] = None
    note: Optional[str] = None


class BookCreate(BookBase):
    pass


class BookRead(BookBase):
    id: int
    is_picked: Optional[int] = None

    class Config:
        from_attributes = True


class ResultBase(BaseModel):
    book_ids: List[int]
    note: Optional[str] = None


class ResultCreate(ResultBase):
    pass


class ResultRead(ResultBase):
    id: int
    created_at: str

    class Config:
        from_attributes = True
