import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .transaction import Transaction


class CategoryDirection(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class Category(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=64, index=True)
    direction: CategoryDirection = Field(default=CategoryDirection.EXPENSE)
    parent_id: uuid.UUID | None = Field(default=None, foreign_key="category.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    archived_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
    )

    parent: Optional["Category"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Category.id"},
    )
    children: list["Category"] = Relationship(back_populates="parent")

    transactions: list["Transaction"] = Relationship(back_populates="category")
    user: "User" = Relationship(back_populates="categories")  # noqa: F821
