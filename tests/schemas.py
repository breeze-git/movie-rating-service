from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReviewDTO(BaseModel):
    id: UUID
    user_id: UUID
    movie_id: UUID
    message: str
    created_at: datetime
    updated_at: datetime
    rating: int

    model_config = ConfigDict(from_attributes=True)


class MovieDTO(BaseModel):
    id: UUID
    director_id: UUID
    title: str
    description: str
    release_year: int
    rating: float | None

    model_config = ConfigDict(from_attributes=True)


class DirectorDTO(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    date_of_birth: date

    model_config = ConfigDict(from_attributes=True)


class UserDTO(BaseModel):
    id: UUID
    username: str
    first_name: str
    last_name: str
    email: str
    hashed_password: str

    model_config = ConfigDict(from_attributes=True)
