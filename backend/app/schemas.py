from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
import re


class BookBase(BaseModel):
    title: str
    author: str | None = None
    description: str | None = None
    target_age: str | None = None
    isbn: str | None = None
    image_url: str | None = None
    note: str | None = None

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        # 数字のみ、13桁
        if not re.match(r"^[0-9]{13}$", v):
            raise ValueError("ISBNは13桁の数字である必要があります")
        return v


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
