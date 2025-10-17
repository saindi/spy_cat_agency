from uuid import UUID

from app import schemas
from app.core.exceptions import BadRequestException
from app.uow.base import ABCUnitOfWork
from app.utils.utils import calc_offset


class MissionService:
    @staticmethod
    async def get_missions(
        sql_uow: ABCUnitOfWork,
        page: int,
        per_page: int,
    ) -> schemas.PaginatedResponse[schemas.Mission]:
        async with sql_uow:
            missions, total_count = await sql_uow.mission.get_multi(
                offset=calc_offset(page, per_page), limit=per_page, return_scheme=True
            )

        return schemas.PaginatedResponse[schemas.Mission](
            items=missions, count=total_count, per_page=per_page
        )

    @staticmethod
    async def create_mission(
        sql_uow: ABCUnitOfWork,
        data: schemas.MissionCreateRequest,
    ) -> schemas.Mission:
        async with sql_uow:
            mission = await sql_uow.mission.create(
                obj_in={"name": data.name, "complete": False}, return_scheme=True
            )

            targets_data = [
                {**data.model_dump(), "mission_id": mission.id} for data in data.targets
            ]

            await sql_uow.target.create_many(obj_in=targets_data)

        return mission

    @staticmethod
    async def get_mission_by_id(
        sql_uow: ABCUnitOfWork,
        mission_id: UUID,
    ) -> schemas.MissionWithTargets:
        filters = {"id": mission_id}

        async with sql_uow:
            mission = await sql_uow.mission.get_mission_with_targets(filters=filters)

        return mission

    @staticmethod
    async def delete_mission(
        sql_uow: ABCUnitOfWork,
        mission_id: UUID,
    ) -> None:
        async with sql_uow:
            filters = {"id": mission_id}

            mission = await sql_uow.mission.get(filters=filters)

            if mission.cat_id:
                raise BadRequestException(
                    "Can't delete a mission that has already been assigned to a cat."
                )

            await sql_uow.mission.delete(filters=filters)

    @staticmethod
    async def assign_cat_to_mission(
        sql_uow: ABCUnitOfWork,
        mission_id: UUID,
        request: schemas.MissionAssignCatRequest,
    ) -> schemas.Mission:
        async with sql_uow:
            mission = await sql_uow.mission.get(filters={"id": mission_id})
            await sql_uow.cat.get(filters={"id": request.cat_id})

            if mission.cat_id:
                raise BadRequestException(f"Mission {mission_id} already has a cat.")

            updated_mission = await sql_uow.mission.update(
                filters={"id": mission_id},
                updates={"cat_id": request.cat_id},
                return_scheme=True,
            )

        return updated_mission

    @staticmethod
    async def update_mission_target(
        sql_uow: ABCUnitOfWork,
        mission_id: UUID,
        target_id: UUID,
        request: schemas.TargetUpdateRequest,
    ) -> schemas.MissionWithTargets:
        async with sql_uow:
            filters = {"id": target_id, "mission_id": mission_id}

            target = await sql_uow.target.get(filters=filters)

            if request.notes is not None:
                if target.complete or request.is_completed is True:
                    raise BadRequestException(
                        "Can't update notes for a completed target."
                    )

            updates = {}

            if request.notes is not None:
                updates["notes"] = request.notes

            if request.is_completed:
                updates["complete"] = True

            if updates:
                await sql_uow.target.update(filters=filters, updates=updates)

            mission = await sql_uow.mission.get_mission_with_targets(
                filters={"id": mission_id}
            )

            if all([target.complete for target in mission.targets]):
                await sql_uow.mission.update(
                    filters={"id": mission_id},
                    updates={"complete": True},
                    return_scheme=True,
                )

                mission.complete = True

        return mission


async def get_mission_service() -> MissionService:
    return MissionService()
