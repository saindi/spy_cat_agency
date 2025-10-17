from uuid import UUID

from fastapi import APIRouter, Query
from starlette import status

from app import schemas
from app.api.dependencies import (
    SQLUnitOfWorkDep,
    cat_service,
)
from app.core.constants.base import PAGINATION_PER_PAGE

from app.schemas import PaginatedResponse

__all__ = ["router"]

router = APIRouter(prefix="/cat", tags=["Spy Cats"])


@router.get(
    "s",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[schemas.Cat],
)
async def get_cats(
    sql_uow: SQLUnitOfWorkDep,
    service: cat_service,
    page: int = Query(1, ge=1),
    per_page: int = Query(PAGINATION_PER_PAGE, ge=1),
) -> PaginatedResponse[schemas.Cat]:
    return await service.get_cats(
        sql_uow=sql_uow,
        page=page,
        per_page=per_page,
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.Cat)
async def create_cat(
    request: schemas.CatCreateRequest,
    sql_uow: SQLUnitOfWorkDep,
    service: cat_service,
) -> schemas.Cat:
    return await service.create_cat(sql_uow=sql_uow, data=request)


@router.get("/{cat_id}", status_code=status.HTTP_200_OK, response_model=schemas.Cat)
async def get_cat(
    sql_uow: SQLUnitOfWorkDep,
    service: cat_service,
    cat_id: UUID,
) -> schemas.Cat:
    return await service.get_cat_by_id(sql_uow=sql_uow, cat_id=cat_id)


@router.patch("/{cat_id}", status_code=status.HTTP_200_OK, response_model=schemas.Cat)
async def update_cat(
    request: schemas.CatUpdateRequest,
    sql_uow: SQLUnitOfWorkDep,
    service: cat_service,
    cat_id: UUID,
) -> schemas.Cat:
    return await service.update_cat(sql_uow=sql_uow, cat_id=cat_id, data=request)


@router.delete("/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cat(
    sql_uow: SQLUnitOfWorkDep,
    service: cat_service,
    cat_id: UUID,
) -> None:
    return await service.delete_cat(sql_uow=sql_uow, cat_id=cat_id)
