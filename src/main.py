import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from core import config
from core.logger import LOGGING
from db.postgres import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Выполнится ДО запуска приложения
    # redis.redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    create_db_and_tables()
    yield
    # Выполнится ПОСЛЕ остановки приложения
    # await redis.redis.close()


app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

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
