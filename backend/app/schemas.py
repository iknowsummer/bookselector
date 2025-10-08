from pydantic import BaseModel, ConfigDict
from datetime import datetime


class BookBase(BaseModel):
    title: str
    author: str | None = None
    description: str | None = None
    target_age: str | None = None
    isbn: str | None = None
    image_url: str | None = None
    note: str | None = None


class BookCreate(BookBase):
    pass


class BookUpdate(BookBase):
    pass


class BookRead(BookBase):
    id: int
    is_picked: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResultBase(BaseModel):
    book_ids: list[int]
    note: str | None = None


class ResultCreate(ResultBase):
    pass


class ResultRead(ResultBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
