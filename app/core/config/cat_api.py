from pydantic import Field

from app.core.config.base import BaseConfig


class CatApiConfig(BaseConfig):
    BREED_URL: str = Field(..., alias="CAT_API_BREED_URL")
