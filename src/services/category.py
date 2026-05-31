import uuid

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.schemas.category import CategoryPublic, CategoryPartialUpdate
from models import Category
from services.exceptions import (
    ParentCategoryDoesNotExists,
    CategoryDirectionMismatch,
    CategoryDoesNotExists,
)
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")


class CategoryService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def validate_category(self, category: Category):
        """
        Цель — проверить валидность категории по следующим правилам:
        1. Родительская категория (если указана) - существует;
        2. Дочерняя категория должна наследовать Category.direction.
        """

        if category.parent_id is not None:
            statement = select(Category).where(Category.id == category.parent_id)
            res = await self.session.exec(statement)
            parent_category = res.one_or_none()
            if parent_category is None:
                raise ParentCategoryDoesNotExists
            if parent_category.direction != category.direction:
                raise CategoryDirectionMismatch

    async def create_category(self, category: Category) -> Category:
        await self.validate_category(category)
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return CategoryPublic.model_validate(category)

    async def get_category(self, category_id: uuid.UUID) -> Category:
        pass

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
        return [
            CategoryPublic.model_validate(category) for category in categories.all()
        ]

    async def update_category(
        self, category_id: uuid.UUID, category: Category
    ) -> Category:
        await self.validate_category(category)
        db_category = await self.session.get(Category, category_id)
        if not db_category:
            raise CategoryDoesNotExists

        update_dict = category.model_dump()

        db_category.sqlmodel_update(update_dict)

        self.session.add(db_category)
        await self.session.commit()
        await self.session.refresh(db_category)
        return CategoryPublic.model_validate(category)

    async def partial_update_category(
        self, category_id: uuid.UUID, category: CategoryPartialUpdate
    ) -> Category:
        await self.validate_category(category)
        db_category = await self.session.get(Category, category_id)
        if not db_category:
            raise CategoryDoesNotExists

        update_dict = category.model_dump(exclude_unset=True, exclude_none=True)
        db_category.sqlmodel_update(update_dict)

        self.session.add(db_category)
        await self.session.commit()
        await self.session.refresh(db_category)
        return CategoryPublic.model_validate(db_category)

    async def delete_category(self, category_id: uuid.UUID) -> bool:
        db_category = await self.session.get(Category, category_id)
        if not db_category:
            raise CategoryDoesNotExists
        await self.session.delete(db_category)
        await self.session.commit()
        return True
