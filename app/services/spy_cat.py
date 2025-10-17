from uuid import UUID

from app import schemas
from app.uow.base import ABCUnitOfWork
from app.utils.utils import calc_offset


class SpyCatsService:
    @staticmethod
    async def get_cats(
        sql_uow: ABCUnitOfWork,
        page: int,
        per_page: int,
    ) -> schemas.PaginatedResponse[schemas.Cat]:
        async with sql_uow:
            cats, total_count = await sql_uow.cat.get_multi(
                offset=calc_offset(page, per_page), limit=per_page, return_scheme=True
            )

        return schemas.PaginatedResponse[schemas.Cat](items=cats, count=total_count, per_page=per_page)

    @staticmethod
    async def create_cat(
        sql_uow: ABCUnitOfWork,
        data: schemas.CatCreateRequest,
    ) -> schemas.Cat:
        await data.validate_breed()

        async with sql_uow:
            new_cat = await sql_uow.cat.create(obj_in=data.model_dump(exclude_none=True), return_scheme=True)

        return new_cat

    @staticmethod
    async def get_cat_by_id(
        sql_uow: ABCUnitOfWork,
        cat_id: UUID,
    ) -> schemas.Cat:
        filters = {"id": cat_id}

        async with sql_uow:
            cat = await sql_uow.cat.get(filters=filters, return_scheme=True)

        return cat

    @staticmethod
    async def update_cat(
        sql_uow: ABCUnitOfWork,
        cat_id: UUID,
        data: schemas.CatUpdateRequest,
    ) -> schemas.Cat:
        async with sql_uow:
            cat = await sql_uow.cat.update(
                filters={"id": cat_id},
                updates=data.model_dump(exclude_none=True),
                return_scheme=True,
            )

        return cat

    @staticmethod
    async def delete_cat(
        sql_uow: ABCUnitOfWork,
        cat_id: UUID,
    ) -> None:
        async with sql_uow:
            await sql_uow.cat.delete(filters={"id": cat_id})


async def get_cat_service() -> SpyCatsService:
    return SpyCatsService()
