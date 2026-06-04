from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from services.exceptions import (
    CategoryDirectionMismatchError,
    CategoryNameDoesNotUniqueError,
    CategoryRecursionParentError,
    ChildCategoryExistsError,
    ObjectDoesNotExistsError,
    OwnerPermissionError,
    ParentCategoryDoesNotExistsError,
    TransactionExistsError,
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

    @app.exception_handler(CategoryDirectionMismatchError)
    async def category_direction_mismatch_handler(
        request: Request, exc: CategoryDirectionMismatchError
    ):
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Category direction inheritance mismatch. "
                "Child category mush inherit category direction."
            },
        )

    @app.exception_handler(CategoryRecursionParentError)
    async def category_recursion_parent_handler(
        request: Request, exc: CategoryRecursionParentError
    ):
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Category cannot be a parent of itself",
            },
        )

    @app.exception_handler(ChildCategoryExistsError)
    async def child_category_exists_handler(
        request: Request, exc: ChildCategoryExistsError
    ):
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Cannot be deleted. Child category exists",
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

    @app.exception_handler(ParentCategoryDoesNotExistsError)
    async def parent_category_does_not_exists_handler(
        request: Request, exc: ParentCategoryDoesNotExistsError
    ):
        return JSONResponse(
            status_code=404,
            content={
                "detail": "Parent category does not exists",
            },
        )

    @app.exception_handler(TransactionExistsError)
    async def transaction_exists_handler(request: Request, exc: TransactionExistsError):
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Cannot be deleted. Transaction exists",
            },
        )

    @app.exception_handler(CategoryNameDoesNotUniqueError)
    async def category_name_does_not_unique_error_handler(
        request: Request, exc: CategoryNameDoesNotUniqueError
    ):
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Cannot be created. Category name has taken",
            },
        )
