from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class IdBase(BaseModel):
    id: UUID


class CreatedAtMixin(BaseModel):
    created_at: datetime


class UpdatedAtMixin(BaseModel):
    updated_at: datetime


class TimestampMixin(CreatedAtMixin, UpdatedAtMixin):
    pass


class IdTimestampMixin(IdBase, TimestampMixin):
    pass
