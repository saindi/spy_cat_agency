from sqlalchemy import Column, ForeignKey, Boolean, UUID, String
from sqlalchemy.orm import relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class Mission(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "missions"

    name = Column(String, index=True)
    cat_id = Column(UUID, ForeignKey("spy_cats.id"), nullable=True, index=True)
    complete = Column(Boolean, default=False, index=True)

    cat = relationship("SpyCat", back_populates="missions")
    targets = relationship(
        "Target", back_populates="mission", cascade="all, delete-orphan"
    )
