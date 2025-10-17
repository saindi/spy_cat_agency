from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.cat import CatRepository
from app.repositories.mission import MissionRepository
from app.repositories.target import TargetRepository


class ABCUnitOfWork(ABC):
    session: AsyncSession

    cat: CatRepository
    target: TargetRepository
    mission: MissionRepository

    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self) -> "ABCUnitOfWork":
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, *args: Any) -> None:
        raise NotImplementedError
