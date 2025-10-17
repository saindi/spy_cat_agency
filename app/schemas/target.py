from uuid import UUID

from pydantic import BaseModel, model_validator

from app.core.exceptions import BadRequestException
from app.schemas.base import IdTimestampMixin


class TargetBase(BaseModel):
    name: str
    country: str
    notes: str


class Target(TargetBase, IdTimestampMixin):
    mission_id: UUID
    complete: bool

    class Config:
        from_attributes = True


class TargetCreateRequest(TargetBase):
    pass


class TargetUpdateRequest(BaseModel):
    notes: str | None = None
    is_completed: bool | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "TargetUpdateRequest":
        if self.notes is None and self.is_completed is None:
            raise BadRequestException("At least one field (notes or is_completed) must be provided.")
        return self
