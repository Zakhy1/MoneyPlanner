import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from models.core.category import CategoryDirection


class CategoryCRUD(SQLModel):
    name: str = Field(max_length=64, index=True)
    direction: CategoryDirection = Field(default=CategoryDirection.EXPENSE)
    parent_id: uuid.UUID | None = Field(default=None, foreign_key="category.id")


class CategoryPublic(CategoryCRUD):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    archived_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
    )


class CategoryPartialUpdate(SQLModel):
    name: str | None = Field(max_length=64, index=True, default=None)
    direction: CategoryDirection | None = Field(default=None)
    parent_id: uuid.UUID | None = Field(default=None, foreign_key="category.id")
    archived_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
    )
