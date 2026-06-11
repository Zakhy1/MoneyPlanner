from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from services.exceptions import (
    ObjectDoesNotExistsError,
    OwnerPermissionError,
    ValidationError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ObjectDoesNotExistsError)
    async def item_not_found_handler(request: Request, exc: ObjectDoesNotExistsError):
        return JSONResponse(
            status_code=404,
            content={
                "detail": f"{exc.name} is not found",
            },
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=400,
            content={
                "detail": exc.reason,
            },
        )

    @app.exception_handler(OwnerPermissionError)
    async def owner_permission_handler(request: Request, exc: OwnerPermissionError):
        return JSONResponse(
            status_code=403,
            content={
                "detail": "Permission denied",
            },
        )
