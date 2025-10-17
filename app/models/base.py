from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(default=func.now(), server_default=func.now(), index=True)


class UpdatedAtMixin:
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now(), server_default=func.now())


class TimestampMixin(CreatedAtMixin, UpdatedAtMixin):
    """Model with created_at and updated_at fields"""


class UUIDMixin:
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, index=True)


class Base(DeclarativeBase):
    type_annotation_map = {
        UUID: postgresql.UUID,
        dict[str, Any]: postgresql.JSON,
        list[dict[str, Any]]: postgresql.ARRAY(postgresql.JSON),
        list[str]: postgresql.ARRAY(String),
        Decimal: postgresql.NUMERIC(10, 2),
        datetime: DateTime(timezone=True),
        bool: Boolean,
    }
