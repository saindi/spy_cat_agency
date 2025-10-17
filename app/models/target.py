from sqlalchemy import Column, ForeignKey, Boolean, String, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class Target(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "targets"

    mission_id = Column(UUID, ForeignKey("missions.id"), index=True)
    name = Column(String, index=True)
    country = Column(String, index=True)
    notes = Column(String, default="")
    complete = Column(Boolean, default=False, index=True)

    mission = relationship("Mission", back_populates="targets")
