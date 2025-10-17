from pydantic import Field

from app.core.config.base import BaseConfig


class DataBaseConfig(BaseConfig):
    USER: str = Field(..., alias="POSTGRES_USER")
    PASSWORD: str = Field(..., alias="POSTGRES_PASSWORD")
    HOST: str = Field(..., alias="POSTGRES_HOST")
    PORT: str = Field(..., alias="POSTGRES_PORT")
    DB: str = Field(..., alias="POSTGRES_DB")
    DATA_VOLUME_NAME: str = "pg_volume"

    POOL_SIZE: int = 50
    MAX_OVERFLOW: int = 10
    POOL_RECYCLE: int = 1800

    @property
    def url(self) -> str:
        """Constructs the SQLAlchemy URL using the database configuration."""
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"
