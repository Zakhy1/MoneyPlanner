import uuid

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from api.schemas.category import CategoryCRUD, CategoryPublic, CategoryPartialUpdate
from api.schemas.message import Message
from core.dependencies.user import get_current_user
from db.postgres import get_session
from models import Category
from services.category import CategoryService
from services.exceptions import (
    ParentCategoryDoesNotExists,
    CategoryDirectionMismatch,
    CategoryDoesNotExists,
    OwnerPermissionError,
)

router = APIRouter()


async def get_category_service(
    session: AsyncSession = Depends(get_session),
):
    return CategoryService(session)


@router.get(
    "/",
)
async def list_category(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, le=100),
    current_user: dict = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
) -> list[CategoryPublic]:
    data = await service.get_list_category(
        page=page, page_size=page_size, user_id=current_user["id"]
    )
    return data


@router.post(
    "/",
)
async def create_category(
    payload: CategoryCRUD,
    current_user: dict = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
) -> CategoryPublic:
    try:
        data = await service.create_category(
            Category(**payload.model_dump() | {"user_id": current_user["id"]})
        )
        return data
    except ParentCategoryDoesNotExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parent category does not exists",
        )
    except CategoryDirectionMismatch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category direction inheritance mismatch. "
            "Child category mush inherit category direction.",
        )
    except OwnerPermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )


@router.put(
    "/{category_id}",
)
async def update_category(
    category_id: uuid.UUID,
    payload: CategoryCRUD,
    current_user: dict = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
) -> CategoryPublic:
    try:
        data = await service.update_category(
            category_id,
            Category(**payload.model_dump() | {"user_id": current_user["id"]}),
            current_user["id"],
        )
        return data
    except ParentCategoryDoesNotExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parent category does not exists",
        )
    except CategoryDoesNotExists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    except CategoryDirectionMismatch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category direction inheritance mismatch. "
            "Child category mush inherit category direction.",
        )
    except OwnerPermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )


@router.patch(
    "/{category_id}",
)
async def partial_update_category(
    category_id: uuid.UUID,
    payload: CategoryPartialUpdate,
    current_user: dict = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
) -> CategoryPublic:
    try:
        data = await service.partial_update_category(
            category_id,
            CategoryPartialUpdate(
                **payload.model_dump() | {"user_id": current_user["id"]},
            ),
            current_user["id"],
        )
        return data
    except ParentCategoryDoesNotExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parent category does not exists",
        )
    except CategoryDoesNotExists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    except CategoryDirectionMismatch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category direction inheritance mismatch. "
            "Child category mush inherit category direction.",
        )
    except OwnerPermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )


@router.delete(
    "/{category_id}",
)
async def delete_category(
    category_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
) -> Message:
    try:
        await service.delete_category(category_id, current_user["id"])
        return Message(message="category deleted")
    except CategoryDoesNotExists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    except OwnerPermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
