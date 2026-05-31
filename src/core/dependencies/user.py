import logging
from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from api.schemas.error import ErrorResponseModel
from db.postgres import get_session
from models import User
from services.auth import decode_token

http_bearer = HTTPBearer(auto_error=False)

logger = logging.getLogger(__name__)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: AsyncSession = Depends(get_session),
    http_bearer=None,
) -> dict[str, Any]:
    if not credentials or not credentials.credentials:
        logger.warning("Access token истек или отсутствует в заголовках")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid access token",
        )

    token = credentials.credentials
    try:
        payload = decode_token(token)

        user_id_str = payload.get("sub")
        if not user_id_str:
            logger.warning("Неверный токен: отсутствует ID пользователя")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
            )

        try:
            user_id = UUID(user_id_str)
        except ValueError:
            logger.warning(
                "Неверный токен: некорректный формат ID пользователя",
                user_id_str=user_id_str,  # type: ignore
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: invalid user ID format",
            )

        user_obj = await db.get(User, user_id)
        if not user_obj:
            logger.warning("Пользователь не найден по ID из токена", user_id=user_id)  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        logger.debug(
            "Текущий пользователь успешно аутентифицирован",
            user_id=user_id,  # type: ignore
            login=user_obj.email,  # type: ignore
        )
        return {
            "id": user_id,
        }

    except ExpiredSignatureError:
        logger.warning("Токен истек")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except JWTError:
        logger.warning("Неверный токен")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    except ValueError as e:
        logger.warning("Ошибка валидации токена", error=str(e))  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorResponseModel(
                detail={"token": "Token is blacklisted"}
            ).model_dump(),
        )
    except Exception:
        logger.exception(
            "Произошла непредвиденная ошибка при получении текущего пользователя"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
