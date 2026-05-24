import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from core import config
from core.logger import LOGGING
from db.postgres import create_db_and_tables
from api.v1 import account
from api.v1 import user


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Выполнится ДО запуска приложения
    # redis.redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    await create_db_and_tables()
    yield
    # Выполнится ПОСЛЕ остановки приложения
    # await redis.redis.close()


app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


app.include_router(account.router, prefix="/api/v1/accounts", tags=["accounts"])
app.include_router(user.router, prefix="/api/v1/auth", tags=["auth"])

if __name__ == "__main__":
    # Приложение может запускаться командой
    # `uvicorn main:app --host 0.0.0.0 --port 8000`
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
