from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class SpyCat(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "spy_cats"

    name = Column(String, index=True)
    years_of_experience = Column(Integer, index=True)
    breed = Column(String, index=True)
    salary = Column(Float)

    missions = relationship("Mission", back_populates="cat")
