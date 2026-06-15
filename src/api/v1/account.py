import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from api.schemas.account import AccountCreate, AccountPatch, AccountRead, AccountUpdate
from core.dependencies.user import get_current_user
from db.postgres import get_session
from models import Account
from services.account import AccountService

router = APIRouter()


async def get_account_service(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return AccountService(session)


@router.get(
    "/",
)
async def list_account(
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[AccountService, Depends(get_account_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
) -> list[AccountRead]:
    data = await service.get_list_account(
        page=page, page_size=page_size, user_id=current_user["id"]
    )
    return [AccountRead.model_validate(account) for account in data]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_account(
    payload: AccountCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[AccountService, Depends(get_account_service)],
) -> AccountRead:
    data = await service.create_account(
        Account(**payload.model_dump() | {"user_id": current_user["id"]})
    )
    return AccountRead.model_validate(data)


@router.put(
    "/{account_id}",
)
async def update_account(
    account_id: uuid.UUID,
    payload: AccountUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[AccountService, Depends(get_account_service)],
) -> AccountRead:
    data = await service.update_account(
        account_id,
        Account(
            **payload.model_dump() | {"user_id": current_user["id"]} | {"id": account_id}
        ),
        current_user["id"],
    )
    return AccountRead.model_validate(data)


@router.patch(
    "/{account_id}",
)
async def partial_update_account(
    account_id: uuid.UUID,
    payload: AccountPatch,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[AccountService, Depends(get_account_service)],
) -> AccountRead:
    data = await service.partial_update_account(
        account_id,
        current_user["id"],
        payload.model_dump(exclude_unset=True),
    )
    return AccountRead.model_validate(data)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: uuid.UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[AccountService, Depends(get_account_service)],
):
    await service.delete_account(account_id, current_user["id"])
