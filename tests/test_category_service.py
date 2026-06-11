import uuid

import pytest

from models import Category
from models.core.category import CategoryDirection
from services.category import CategoryService
from services.exceptions import CategoryRecursionParentError


class FakeSession:
    def __init__(self, categories: list[Category]):
        self.categories = {category.id: category for category in categories}

    async def get(self, model, category_id):
        return self.categories.get(category_id)


def make_category(
    *,
    category_id: uuid.UUID | None = None,
    user_id: uuid.UUID,
    parent_id: uuid.UUID | None = None,
) -> Category:
    return Category(
        id=category_id or uuid.uuid4(),
        name="Category",
        direction=CategoryDirection.EXPENSE,
        parent_id=parent_id,
        user_id=user_id,
    )


@pytest.mark.asyncio
async def test_validate_category_rejects_ancestor_parent_cycle():
    user_id = uuid.uuid4()
    category_a = make_category(user_id=user_id)
    category_b = make_category(user_id=user_id, parent_id=category_a.id)
    category_c = make_category(user_id=user_id, parent_id=category_b.id)
    updated_category_a = make_category(
        category_id=category_a.id,
        user_id=user_id,
        parent_id=category_c.id,
    )
    service = CategoryService(FakeSession([category_a, category_b, category_c]))

    with pytest.raises(CategoryRecursionParentError):
        await service.validate_category(updated_category_a)


@pytest.mark.asyncio
async def test_validate_category_allows_acyclic_parent_chain():
    user_id = uuid.uuid4()
    category_a = make_category(user_id=user_id)
    category_b = make_category(user_id=user_id, parent_id=category_a.id)
    category_c = make_category(user_id=user_id, parent_id=category_b.id)
    service = CategoryService(FakeSession([category_a, category_b]))

    await service.validate_category(category_c)
