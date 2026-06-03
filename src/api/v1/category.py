import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from api.schemas.category import CategoryCRUD, CategoryPartialUpdate, CategoryPublic
from api.schemas.message import Message
from core.dependencies.user import get_current_user
from db.postgres import get_session
from models import Category
from services.category import CategoryService
from services.exceptions import (
    CategoryDirectionMismatchError,
    CategoryDoesNotExistsError,
    CategoryRecursionParentError,
    ChildCategoryExistsError,
    OwnerPermissionError,
    ParentCategoryDoesNotExistsError,
)

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
) -> list[CategoryPublic]:
    data = await service.get_list_category(
        page=page, page_size=page_size, user_id=current_user["id"]
    )
    return [CategoryPublic.model_validate(category) for category in data]


@router.post(
    "/",
)
async def create_category(
    payload: CategoryCRUD,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryPublic:
    try:
        data = await service.create_category(
            Category(**payload.model_dump() | {"user_id": current_user["id"]})
        )
        return CategoryPublic.model_validate(data)
    except ParentCategoryDoesNotExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parent category does not exists",
        )
    except CategoryDirectionMismatchError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category direction inheritance mismatch. "
            "Child category mush inherit category direction.",
        )
    except OwnerPermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    except CategoryRecursionParentError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сategory cannot be a parent of itself",
        )


@router.put(
    "/{category_id}",
)
async def update_category(
    category_id: uuid.UUID,
    payload: CategoryCRUD,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryPublic:
    try:
        data = await service.update_category(
            category_id,
            Category(
                **payload.model_dump()
                | {"user_id": current_user["id"]}
                | {"id": category_id}
            ),
            current_user["id"],
        )
        return CategoryPublic.model_validate(data)
    except ParentCategoryDoesNotExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parent category does not exists",
        )
    except CategoryDoesNotExistsError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    except CategoryDirectionMismatchError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category direction inheritance mismatch. "
            "Child category mush inherit category direction.",
        )
    except OwnerPermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    except CategoryRecursionParentError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сategory cannot be a parent of itself",
        )


@router.patch(
    "/{category_id}",
)
async def partial_update_category(
    category_id: uuid.UUID,
    payload: CategoryPartialUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryPublic:
    try:
        data = await service.partial_update_category(
            category_id,
            current_user["id"],
            payload.model_dump(exclude_unset=True),
        )
        return CategoryPublic.model_validate(data)
    except ParentCategoryDoesNotExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parent category does not exists",
        )
    except CategoryDoesNotExistsError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    except CategoryDirectionMismatchError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category direction inheritance mismatch. "
            "Child category mush inherit category direction.",
        )
    except OwnerPermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can't edit other categories",
        )
    except CategoryRecursionParentError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сategory cannot be a parent of itself",
        )


@router.delete(
    "/{category_id}",
)
async def delete_category(
    category_id: uuid.UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> Message:
    try:
        await service.delete_category(category_id, current_user["id"])
        return Message(message="category deleted")
    except CategoryDoesNotExistsError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    except OwnerPermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    except ChildCategoryExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot be deleted. Child category exists",
        )
