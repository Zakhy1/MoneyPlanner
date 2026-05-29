from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from api.schemas.category import CategoryCreate, CategoryPublic
from core.dependencies.user import get_current_user
from db.postgres import get_session
from models import Category

router = APIRouter()


@router.get(
    "/",
)
async def list_category(
    session: AsyncSession = Depends(get_session),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, le=100),
    current_user: dict = Depends(get_current_user),
) -> list[Category]:
    offset_value = (page - 1) * page_size
    statement = (
        select(Category)
        .where(Category.user_id == current_user["id"])
        .offset(offset_value)
        .limit(page_size)
    )
    categories = await session.exec(statement)
    return categories.all()


@router.post(
    "/",
)
async def create_category(
    payload: CategoryCreate,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    category = Category(**payload.model_dump() | {"user_id": current_user["id"]})
    if category.parent_id is not None:
        statement = select(Category).where(Category.id == category.parent_id)
        parent_category = await session.exec(statement)
        res = parent_category.one_or_none()
        if res is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent category does not exists",
            )
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return CategoryPublic.model_validate(category)
