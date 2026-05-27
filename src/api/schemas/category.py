import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from models.core.category import CategoryDirection


class CategoryCreate(SQLModel):
    name: str = Field(max_length=64, index=True)
    direction: CategoryDirection = Field(default=CategoryDirection.EXPENSE)
    parent_id: uuid.UUID | None = Field(default=None, foreign_key="category.id")


class CategoryPublic(CategoryCreate):
    archived_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
    )
