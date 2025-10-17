from app import models, schemas
from app.repositories.base import RepositoryMixin


class TargetRepository(RepositoryMixin[models.Target, schemas.Target]):
    model = models.Target
    schema = schemas.Target
