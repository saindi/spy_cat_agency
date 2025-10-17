from typing import Annotated

from fastapi import Depends

from app.services.mission import get_mission_service
from app.services.spy_cat import SpyCatsService, get_cat_service
from app.uow.base import ABCUnitOfWork
from app.uow.sql import SQLUnitOfWork

__all__ = [
    "SQLUnitOfWorkDep",
    "cat_service",
    "mission_service",
    "target_service",
]


SQLUnitOfWorkDep = Annotated[ABCUnitOfWork, Depends(SQLUnitOfWork)]

cat_service = Annotated[SpyCatsService, Depends(get_cat_service)]
mission_service = Annotated[SpyCatsService, Depends(get_mission_service)]
target_service = Annotated[SpyCatsService, Depends(get_mission_service)]
