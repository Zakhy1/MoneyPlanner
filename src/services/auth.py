from sqlmodel.ext.asyncio.session import AsyncSession

from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.hash import bcrypt

from core import config


def hash_password(password: str) -> str:
    return bcrypt.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.verify(password, password_hash)


def create_token(sub: str, minutes: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=minutes)).timestamp()),
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALG)


def decode_token(token: str) -> dict:
    return jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALG])


class AuthService:
    def __init__(self, session: AsyncSession):
        pass
