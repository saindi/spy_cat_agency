from typing import TypeVar, Generic, Any

from pydantic import BaseModel, Field, model_validator

from app.core.constants.base import PAGINATION_PER_PAGE


__all__ = ["PaginatedResponse", "ItemsResponse", "PaginatedResponseWithUnreadCount"]


M = TypeVar("M")


class PaginateBase(BaseModel):
    count: int = Field(description="Number of total items")
    total_pages: int = Field(default=0, description="Number of total pages")
    per_page: int = Field(default=PAGINATION_PER_PAGE, description="Items per page")


class PaginatedResponse(PaginateBase, Generic[M]):
    items: list[M] = Field(default_factory=list, description="List of paginated items")

    @model_validator(mode="before")
    @classmethod
    def calculate_pagination(cls, values: dict[str, Any]) -> dict[str, Any]:
        count = values.get("count", 0)
        per_page = values.get("per_page", PAGINATION_PER_PAGE)
        if not per_page:
            per_page = len(values.get("items", [])) or 1
        values["total_pages"] = (count + per_page - 1) // per_page
        return values


class ItemsResponse(BaseModel, Generic[M]):
    items: list[M] = Field(default_factory=list, description="List of items")


class PaginatedResponseWithUnreadCount(PaginatedResponse[M]):
    unread_count: int = Field(description="Number of unread notifications")
