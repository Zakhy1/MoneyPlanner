import uuid
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Index
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .transaction import Transaction


class CategoryDirection(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class Category(SQLModel, table=True):
    __table_args__ = (
        Index(
            "idx_user_category_unique",
            "user_id",
            "name",
            unique=True,
        ),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=64)
    direction: CategoryDirection = Field(default=CategoryDirection.EXPENSE)
    parent_id: uuid.UUID | None = Field(default=None, foreign_key="category.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")

    archived: bool = Field(default=False)

    parent: Optional["Category"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Category.id"},
    )
    children: list["Category"] = Relationship(back_populates="parent")

    transactions: list["Transaction"] = Relationship(back_populates="category")
    user: "User" = Relationship(back_populates="categories")  # noqa: F821
