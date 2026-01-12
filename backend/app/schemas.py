from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from enum import Enum
import re


def validate_isbn_format(v: str | None) -> str | None:
    """
    ISBNフォーマットを検証する共通関数

    Args:
        v: ISBN文字列またはNone

    Returns:
        str | None: 検証済みのISBN文字列またはNone

    Raises:
        ValueError: ISBNが13桁の数字でない場合
    """
    if v is None or v == "":
        return None
    # 数字のみ、13桁
    if not re.match(r"^[0-9]{13}$", v):
        raise ValueError("ISBNは13桁の数字である必要があります")
    return v


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
    shelf_id: int | None = None

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, v: str | None) -> str | None:
        return validate_isbn_format(v)


class BookCreate(BaseModel):
    isbn: str

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, v: str | None) -> str | None:
        return validate_isbn_format(v)

    model_config = ConfigDict(extra="forbid")


class BookUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")


class BookRead(BookBase):
    id: int
    status: BookStatus = BookStatus.UNREAD
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# UserBook スキーマ
class UserBookBase(BaseModel):
    note: str | None = None
    status: BookStatus = BookStatus.UNREAD
    shelf_id: int | None = None


class UserBookCreate(UserBookBase):
    book_id: int


class UserBookUpdate(BaseModel):
    note: str | None = None
    status: BookStatus | None = None
    shelf_id: int | None = None


class UserBookRead(UserBookBase):
    id: int
    user_id: int
    book_id: int
    created_at: datetime
    updated_at: datetime

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
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    name: str
    auth0_sub: str | None = None
    email: str | None = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: str | None = None
    auth0_sub: str | None = None
    email: str | None = None


class UserRead(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
