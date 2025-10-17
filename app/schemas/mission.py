from uuid import UUID

from pydantic import BaseModel

from app.schemas.target import Target, TargetCreateRequest
from app.schemas.base import IdTimestampMixin


class Mission(IdTimestampMixin):
    cat_id: UUID | None
    name: str
    complete: bool

    class Config:
        from_attributes = True


class MissionCreateRequest(BaseModel):
    name: str
    targets: list[TargetCreateRequest]


class MissionWithTargets(Mission):
    targets: list[Target]


class MissionAssignCatRequest(BaseModel):
    cat_id: UUID
