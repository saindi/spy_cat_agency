from typing import Annotated

from fastapi import Depends

from app.services.mission import get_mission_service, MissionService
from app.services.spy_cat import SpyCatsService, get_cat_service
from app.uow.base import ABCUnitOfWork
from app.uow.sql import SQLUnitOfWork

__all__ = [
    "SQLUnitOfWorkDep",
    "cat_service",
    "mission_service",
]


SQLUnitOfWorkDep = Annotated[ABCUnitOfWork, Depends(SQLUnitOfWork)]

cat_service = Annotated[SpyCatsService, Depends(get_cat_service)]
mission_service = Annotated[MissionService, Depends(get_mission_service)]
