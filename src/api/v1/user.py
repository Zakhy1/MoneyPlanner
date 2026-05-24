import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from db.postgres import get_session
from models import User
from pydantic import BaseModel, EmailStr

from services.auth import hash_password, verify_password, create_token, decode_token

from services.auth import AuthService

router = APIRouter()

security = HTTPBearer()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access: str
    refresh: str


class RefreshToken(BaseModel):
    refresh: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Me(BaseModel):
    id: uuid.UUID
    email: EmailStr


async def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    return AuthService(session)


@router.post("/register")
async def register(
    payload: RegisterRequest, session: AsyncSession = Depends(get_session)
):
    res = await session.exec(select(User).where(User.email == payload.email))
    if res.one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=payload.email, password=hash_password(payload.password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return Me(id=user.id, email=user.email)


@router.post("/login", response_model=TokenPair)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    res = await session.exec(select(User).where(User.email == payload.email))
    user = res.one_or_none()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenPair(
        access=create_token(str(user.id), minutes=30),
        refresh=create_token(str(user.id), minutes=43200),
    )


@router.get("/me", response_model=Me)
async def me(
    token: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    try:
        payload = decode_token(token.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload["sub"]
    res = await session.exec(select(User).where(User.id == user_id))
    user = res.one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    return Me(id=user.id, email=user.email)


# @router.post(
#     "/logout",
#     response_model=MessageResponse,
#     responses={200: {"model": MessageResponse, "description": "Logged out"}},
#     summary="Log out from current session",
#     description="Invalidates the provided refresh token, effectively logging out the user from this session.",
#     # dependencies=[Depends(lambda: rate_limit_dependency(traffic_type="default"))]
# )
# async def logout(
#     request_data: RefreshToken, auth_service: AuthService = Depends(get_auth_service)
# ) -> MessageResponse:
#     await auth_service.logout(request_data.refresh_token)
#     return MessageResponse(message="Logged out")


# @router.post(
#     "/refresh",
#     response_model=TokenPair,
#     responses={
#         status.HTTP_200_OK: {"model": TokenPair},
#         status.HTTP_401_UNAUTHORIZED: {
#             "description": "Invalid or expired refresh token",
#             "model": ErrorResponseModel,
#         },
#     },
#     summary="Refresh access token",
#     description="Exchanges a valid refresh token for a new access token and refresh token.",
#     # dependencies=[Depends(lambda: rate_limit_dependency(traffic_type="default"))]
# )
# async def refresh_token(
#     request_data: RefreshToken, auth_service: AuthService = Depends(get_auth_service)
# ) -> TokenPair:
#     try:
#         new_tokens = await re(request_data.refresh_token)
#         if not new_tokens:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail=ErrorResponseModel(
#                     detail={"token": "Invalid or expired refresh token"}
#                 ).model_dump(),
#             )
#         return new_tokens
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=ErrorResponseModel(detail={"token": str(e)}).model_dump(),
#         )
