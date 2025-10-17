from pydantic import Field, BaseModel

from app.core.exceptions import BadRequestException
from app.schemas.base import IdTimestampMixin
from app.services.cat_api import cat_api_service


class Cat(IdTimestampMixin):
    name: str
    years_of_experience: int
    breed: str
    salary: float

    class Config:
        from_attributes = True


class CatCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, description="Name of the spy cat")
    years_of_experience: int = Field(..., ge=0, description="Years of experience, >= 0")
    breed: str = Field(..., min_length=3, description="Breed of the cat")
    salary: float = Field(..., ge=0, description="Salary of the cat, >= 0")

    async def validate_breed(self) -> None:
        is_valid_breed = await cat_api_service.is_valid_breed(self.breed)

        if not is_valid_breed:
            raise BadRequestException(f"Invalid breed: {self.breed}. Please, check your request.")


class CatUpdateRequest(BaseModel):
    salary: float = Field(..., ge=0, description="Salary of the cat, >= 0")
