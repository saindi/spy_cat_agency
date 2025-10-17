from typing import Any

from sqlalchemy.orm import selectinload

from app import models, schemas
from app.repositories.base import RepositoryMixin


class MissionRepository(RepositoryMixin[models.Mission, schemas.Mission]):
    model = models.Mission
    schema = schemas.Mission

    async def get_mission_with_targets(self, filters: dict[str, Any]) -> schemas.MissionWithTargets:
        db_mission = await self.get(
            filters=filters,
            options=[selectinload(models.Mission.targets)],
            return_scheme=False,
        )

        return self._convert_with_targets(db_mission=db_mission)

    def _convert_with_targets(self, db_mission: models.Mission) -> schemas.MissionWithTargets:
        return schemas.MissionWithTargets.model_validate(db_mission)
