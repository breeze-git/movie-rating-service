from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.fields import Use

from app.schemas.auth import UserRegister
from app.schemas.users import UserUpdate


class UserRegisterFactory(ModelFactory[UserRegister]):
    __model__ = UserRegister

    password = "StrongPassword123!"

    username = Use(ModelFactory.__faker__.user_name)
    first_name = Use(ModelFactory.__faker__.first_name)
    last_name = Use(ModelFactory.__faker__.last_name)
    email = Use(ModelFactory.__faker__.email)


class UserUpdateFactory(ModelFactory[UserUpdate]):
    __model__ = UserUpdate

    username = Use(ModelFactory.__faker__.user_name)
    first_name = Use(ModelFactory.__faker__.first_name)
    last_name = Use(ModelFactory.__faker__.last_name)
