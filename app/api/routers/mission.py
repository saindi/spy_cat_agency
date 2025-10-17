from uuid import UUID

from fastapi import APIRouter, Query
from starlette import status

from app import schemas
from app.api.dependencies import (
    SQLUnitOfWorkDep,
    mission_service,
)
from app.core.constants.base import PAGINATION_PER_PAGE

from app.schemas import PaginatedResponse

__all__ = ["router"]

router = APIRouter(prefix="/mission", tags=["Missions"])


@router.get(
    "s",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[schemas.Mission],
)
async def get_missions(
    sql_uow: SQLUnitOfWorkDep,
    service: mission_service,
    page: int = Query(1, ge=1),
    per_page: int = Query(PAGINATION_PER_PAGE, ge=1),
) -> PaginatedResponse[schemas.Mission]:
    return await service.get_missions(
        sql_uow=sql_uow,
        page=page,
        per_page=per_page,
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.Mission)
async def create_mission(
    request: schemas.MissionCreateRequest,
    sql_uow: SQLUnitOfWorkDep,
    service: mission_service,
) -> schemas.Mission:
    return await service.create_mission(sql_uow=sql_uow, data=request)


@router.get(
    "/{mission_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MissionWithTargets,
)
async def get_mission(
    sql_uow: SQLUnitOfWorkDep,
    service: mission_service,
    mission_id: UUID,
) -> schemas.MissionWithTargets:
    return await service.get_mission_by_id(sql_uow=sql_uow, mission_id=mission_id)


@router.delete("/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mission(
    sql_uow: SQLUnitOfWorkDep,
    service: mission_service,
    mission_id: UUID,
) -> None:
    return await service.delete_mission(sql_uow=sql_uow, mission_id=mission_id)


@router.post(
    "/{mission_id}/assign-cat",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Mission,
)
async def assign_cat_to_mission(
    sql_uow: SQLUnitOfWorkDep,
    service: mission_service,
    mission_id: UUID,
    request: schemas.MissionAssignCatRequest,
) -> schemas.Mission:
    return await service.assign_cat_to_mission(
        sql_uow=sql_uow, mission_id=mission_id, request=request
    )


@router.patch(
    "/{mission_id}/target/{target_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MissionWithTargets,
)
async def update_mission_target(
    sql_uow: SQLUnitOfWorkDep,
    service: mission_service,
    mission_id: UUID,
    target_id: UUID,
    request: schemas.TargetUpdateRequest,
) -> schemas.MissionWithTargets:
    return await service.update_mission_target(
        sql_uow=sql_uow, mission_id=mission_id, target_id=target_id, request=request
    )
