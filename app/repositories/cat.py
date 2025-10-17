from app import models, schemas
from app.repositories.base import RepositoryMixin


class CatRepository(RepositoryMixin[models.SpyCat, schemas.Cat]):
    model = models.SpyCat
    schema = schemas.Cat
