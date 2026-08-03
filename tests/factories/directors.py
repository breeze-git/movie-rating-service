from datetime import date

from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.fields import Use

from app.schemas.directors import DirectorBase


class DirectorBaseFactory(ModelFactory[DirectorBase]):
    __model__ = DirectorBase

    date_of_birth: date = date(year=1976, month=10, day=9)

    first_name = Use(ModelFactory.__faker__.first_name)
    last_name = Use(ModelFactory.__faker__.last_name)
