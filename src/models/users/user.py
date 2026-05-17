import uuid
from datetime import datetime, UTC
from enum import Enum

from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel, AutoString


class UserStatus(str, Enum):
    DEFAULT = "default"
    PREMIUM = "premium"


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: EmailStr = Field(sa_type=AutoString, unique=True, index=True)
    status: UserStatus = Field(default=UserStatus.DEFAULT)
    password: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(UTC),
    )

    accounts: list["Account"] = Relationship(  # noqa: F821
        back_populates="user",
    )
    categories: list["Category"] = Relationship(back_populates="user")  # noqa: F821
