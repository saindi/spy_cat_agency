from typing import Any

from loguru import logger

from app.infra.database import get_session_maker
from app.repositories.cat import CatRepository
from app.repositories.mission import MissionRepository
from app.repositories.target import TargetRepository
from app.uow.base import ABCUnitOfWork


class SQLUnitOfWork(ABCUnitOfWork):
    def __init__(self) -> None:
        self.session_maker = get_session_maker()

    async def __aenter__(self) -> "SQLUnitOfWork":
        self.session = self.session_maker()

        self.cat = CatRepository(session=self.session)
        self.target = TargetRepository(session=self.session)
        self.mission = MissionRepository(session=self.session)

        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if exc:
            logger.exception(
                "An error occurred while processing the request. Rolling back. Error: {exc}",
                exc=exc,
            )
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()
        await logger.complete()

        if exc:
            raise exc

    async def rollback(self) -> None:
        await self.session.rollback()
