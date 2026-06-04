import uuid
from typing import Any

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import Category, Transaction
from services.exceptions import (
    CategoryDirectionMismatchError,
    CategoryDoesNotExistsError,
    CategoryNameDoesNotUniqueError,
    CategoryRecursionParentError,
    ChildCategoryExistsError,
    OwnerPermissionError,
    ParentCategoryDoesNotExistsError,
    TransactionExistsError,
)


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
        * Существует категория с таким же именем
        * Родительская категория (если указана) - существует;
        * Дочерняя категория должна наследовать Category.direction;
        * Родительская категория должна принадлежать текущему пользователю;
        * Категория не ссылается на саму себя через цепочку родителей.
        """
        statement = select(Category).where(
            Category.user_id == category.user_id, Category.name == category.name
        )
        existing_category = await self.session.exec(statement)
        if existing_category.first() is not None:
            raise CategoryNameDoesNotUniqueError
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
            await self._check_parent_chain(parent_category, category.id)

    async def _check_parent_chain(
        self, parent_category: Category, category_id: uuid.UUID
    ) -> None:
        visited_category_ids = {category_id}
        current_category = parent_category

        while current_category is not None:
            if current_category.id in visited_category_ids:
                raise CategoryRecursionParentError
            visited_category_ids.add(current_category.id)

            if current_category.parent_id is None:
                return

            current_category = await self.session.get(
                Category, current_category.parent_id
            )
            if current_category is None:
                raise ParentCategoryDoesNotExistsError

    async def create_category(self, category: Category) -> Category:
        await self.validate_category(category)
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category

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
            .order_by(Category.name)
            .offset(offset_value)
            .limit(page_size)
        )
        categories = await self.session.exec(statement)
        return categories.all()

    async def update_category(
        self, category_id: uuid.UUID, category: Category, user_id: uuid.UUID
    ) -> Category:
        db_category = await self.get_category(category_id)
        await self.check_owner(db_category, user_id)
        await self.validate_category(category)
        update_dict = category.model_dump()

        db_category.sqlmodel_update(update_dict)

        self.session.add(db_category)
        await self.session.commit()
        await self.session.refresh(db_category)
        return db_category

    async def partial_update_category(
        self,
        category_id: uuid.UUID,
        user_id: uuid.UUID,
        update_data: dict[str, Any],
    ) -> Category:
        db_category = await self.get_category(category_id)

        # Проверка
        candidate = db_category.model_copy(update=update_data)
        await self.validate_category(candidate)
        await self.check_owner(db_category, user_id)

        for key, value in update_data.items():
            if key not in ["name", "direction", "parent_id", "archived"]:
                continue
            setattr(db_category, key, value)

        self.session.add(db_category)
        await self.session.commit()
        await self.session.refresh(db_category)
        return db_category

    async def delete_category(self, category_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        db_category = await self.get_category(category_id)
        await self.check_owner(db_category, user_id)
        # Ищем потомков
        statement = select(Category).where(Category.parent_id == category_id)
        result = await self.session.exec(statement)
        child_category = result.first()
        if child_category is not None:
            raise ChildCategoryExistsError
        # Ищем транзакции
        statement = select(Transaction).where(Transaction.category_id == category_id)
        result = await self.session.exec(statement)
        if result.first():
            raise TransactionExistsError
        await self.session.delete(db_category)
        await self.session.commit()
        return True
