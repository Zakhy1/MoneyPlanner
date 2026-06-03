import uuid
import warnings
from typing import Any

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.schemas.category import CategoryPublic
from models import Category
from services.exceptions import (
    CategoryDirectionMismatchError,
    CategoryDoesNotExistsError,
    CategoryRecursionParentError,
    ChildCategoryExistsError,
    OwnerPermissionError,
    ParentCategoryDoesNotExistsError,
)

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")


class CategoryService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_owner(self, category: Category, user_id: uuid.UUID):
        if category.user_id != user_id:
            raise OwnerPermissionError

    async def get_category(self, category_id: uuid.UUID):
        db_category = await self.session.get(Category, category_id)
        if db_category is None:
            raise CategoryDoesNotExistsError
        return db_category

    async def validate_category(self, category: Category):
        """
        Цель — проверить валидность категории по следующим правилам:
        1. Родительская категория (если указана) - существует;
        2. Дочерняя категория должна наследовать Category.direction;
        3. Родительская категория должна принадлежать текущему пользователю;
        4. Категория не ссылается на саму себя.
        """

        if category.parent_id is not None:
            parent_category = await self.session.get(Category, category.parent_id)
            if parent_category is None:
                raise ParentCategoryDoesNotExistsError
            if parent_category.direction != category.direction:
                raise CategoryDirectionMismatchError
            if parent_category.user_id != category.user_id:
                raise OwnerPermissionError
            if parent_category.id == category.id:
                raise CategoryRecursionParentError

    async def create_category(self, category: Category) -> Category:
        await self.validate_category(category)
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return CategoryPublic.model_validate(category)

    async def get_list_category(
        self, page_size: int, page: int, user_id: uuid.UUID
    ) -> list[Category]:
        """
        :param page_size:
        :param page:
        :param user_id:
        :return: list Category
        """
        offset_value = (page - 1) * page_size
        statement = (
            select(Category)
            .where(Category.user_id == user_id)
            .offset(offset_value)
            .limit(page_size)
        )
        categories = await self.session.exec(statement)
        return [CategoryPublic.model_validate(category) for category in categories.all()]

    async def update_category(
        self, category_id: uuid.UUID, category: Category, user_id: uuid.UUID
    ) -> Category:
        db_category = await self.get_category(category_id)
        if not db_category:
            raise CategoryDoesNotExistsError
        await self.check_owner(db_category, user_id)
        await self.validate_category(category)
        update_dict = category.model_dump()

        db_category.sqlmodel_update(update_dict)

        self.session.add(db_category)
        await self.session.commit()
        await self.session.refresh(db_category)
        return CategoryPublic.model_validate(db_category)

    async def partial_update_category(
        self,
        category_id: uuid.UUID,
        user_id: uuid.UUID,
        update_data: dict[str, Any],
    ) -> Category:
        db_category = await self.get_category(category_id)
        for key, value in update_data.items():
            setattr(db_category, key, value)
        await self.check_owner(db_category, user_id)
        await self.validate_category(db_category)
        if not db_category:
            raise CategoryDoesNotExistsError

        self.session.add(db_category)
        await self.session.commit()
        await self.session.refresh(db_category)
        return CategoryPublic.model_validate(db_category)

    async def delete_category(self, category_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        db_category = await self.get_category(category_id)
        await self.check_owner(db_category, user_id)
        if not db_category:
            raise CategoryDoesNotExistsError
        statement = select(Category).where(Category.parent_id == category_id)
        result = await self.session.exec(statement)
        child_category = result.first()
        if child_category is not None:
            raise ChildCategoryExistsError
        await self.session.delete(db_category)
        await self.session.commit()
        return True
