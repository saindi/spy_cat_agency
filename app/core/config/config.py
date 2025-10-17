from typing import Literal


from app.core.config.base import BaseConfig
from app.core.config.cat_api import CatApiConfig
from app.core.config.db import DataBaseConfig


class Settings(BaseConfig):
    SERVER_HOST: str
    SERVER_PORT: int
    RELOAD: bool = False
    EXECUTION_MODE: Literal["PRODUCTION", "DEVELOPMENT"] = "DEVELOPMENT"

    ALLOW_ORIGINS: list[str]

    db: DataBaseConfig = DataBaseConfig()
    cat_api: CatApiConfig = CatApiConfig()

    @property
    def is_production(self) -> bool:
        return self.EXECUTION_MODE == "PRODUCTION"


settings = Settings()
