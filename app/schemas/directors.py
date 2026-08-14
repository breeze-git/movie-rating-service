from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.validators import NonEmptyString, Over7YearsOld


class DirectorBase(BaseModel):
    first_name: NonEmptyString = Field(max_length=50)
    last_name: NonEmptyString = Field(max_length=50)
    date_of_birth: Over7YearsOld


class DirectorDetail(DirectorBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class DirectorUpdate(BaseModel):
    first_name: NonEmptyString | None = Field(default=None, max_length=50)
    last_name: NonEmptyString | None = Field(default=None, max_length=50)
    date_of_birth: Over7YearsOld | None = None
