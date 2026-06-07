import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from api.schemas.category import (
    CategoryCreate,
    CategoryPatch,
    CategoryRead,
    CategoryUpdate,
)
from core.dependencies.user import get_current_user
from db.postgres import get_session
from models import Category
from services.category import CategoryService

router = APIRouter()


async def get_category_service(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return CategoryService(session)


@router.get(
    "/",
)
async def list_category(
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[CategoryService, Depends(get_category_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
) -> list[CategoryRead]:
    data = await service.get_list_category(
        page=page, page_size=page_size, user_id=current_user["id"]
    )
    return [CategoryRead.model_validate(category) for category in data]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryRead:
    data = await service.create_category(
        Category(**payload.model_dump() | {"user_id": current_user["id"]})
    )
    return CategoryRead.model_validate(data)


@router.put(
    "/{category_id}",
)
async def update_category(
    category_id: uuid.UUID,
    payload: CategoryUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryRead:
    data = await service.update_category(
        category_id,
        Category(
            **payload.model_dump() | {"user_id": current_user["id"]} | {"id": category_id}
        ),
        current_user["id"],
    )
    return CategoryRead.model_validate(data)


@router.patch(
    "/{category_id}",
)
async def partial_update_category(
    category_id: uuid.UUID,
    payload: CategoryPatch,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryRead:
    data = await service.partial_update_category(
        category_id,
        current_user["id"],
        payload.model_dump(exclude_unset=True),
    )
    return CategoryRead.model_validate(data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: uuid.UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[CategoryService, Depends(get_category_service)],
):
    await service.delete_category(category_id, current_user["id"])
