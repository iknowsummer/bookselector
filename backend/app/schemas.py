from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from enum import Enum
import re


class BookStatus(str, Enum):
    """
    書籍の読書ステータス
    """

    UNREAD = "unread"  # 未読
    PICKED = "picked"  # 選択済み
    READ = "read"  # 読了


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


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    description: str | None = None
    target_age: str | None = None
    isbn: str | None = None
    image_url: str | None = None
    note: str | None = None
    status: BookStatus | None = None

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        # 数字のみ、13桁
        if not re.match(r"^[0-9]{13}$", v):
            raise ValueError("ISBNは13桁の数字である必要があります")
        return v


class BookRead(BookBase):
    id: int
    status: BookStatus = BookStatus.UNREAD
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ShelfBase(BaseModel):
    name: str
    memo: str | None = None


class ShelfCreate(ShelfBase):
    pass


class ShelfUpdate(BaseModel):
    name: str | None = None
    memo: str | None = None


class ShelfRead(ShelfBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
