from collections.abc import Callable

import pytest
import pytest_asyncio
from httpx2 import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_hash
from app.database.models import Role, User
from app.main import app
from app.schemas.auth import Tokens, UserRegister
from tests.factories.users import UserRegisterFactory


@pytest.fixture
def register_payload():
    return UserRegisterFactory.build()


@pytest.fixture
def create_user_in_db(db_session: AsyncSession) -> Callable:
    async def _create_user(payload: UserRegister, roles: tuple[str] = ("user",)) -> User:
        hashed_password = get_hash(payload.password).decode("utf-8")

        query = select(Role).where(Role.name.in_(roles))

        default_roles = (await db_session.scalars(query)).all()

        user = User(
            **payload.model_dump(exclude={"password"}),
            hashed_password=hashed_password,
            roles=default_roles,
        )

        db_session.add(user)

        await db_session.commit()

        return user

    return _create_user


@pytest_asyncio.fixture
async def registered_user_payload(create_user_in_db: Callable, register_payload: UserRegister) -> UserRegister:
    await create_user_in_db(register_payload)

    return register_payload


@pytest_asyncio.fixture
async def registered_admin_payload(create_user_in_db: Callable, register_payload: UserRegister) -> UserRegister:
    await create_user_in_db(register_payload, roles=("admin",))

    return register_payload


@pytest.fixture
def login_user(
    api_client: AsyncClient,
) -> Callable:
    async def _login(
        payload: UserRegister,
    ):
        login_data = {
            "username": payload.email,
            "password": payload.password,
        }

        endpoint_url = app.url_path_for("login_user")

        response = await api_client.post(endpoint_url, data=login_data)

        return response.json()["data"]

    return _login


@pytest_asyncio.fixture
async def user_tokens(
    registered_user_payload: UserRegister,
    login_user: Callable,
) -> Tokens:
    tokens_raw = await login_user(registered_user_payload)

    return Tokens.model_validate(tokens_raw)


@pytest_asyncio.fixture
async def admin_tokens(
    registered_admin_payload: UserRegister,
    login_user: Callable,
) -> Tokens:
    tokens_raw = await login_user(registered_admin_payload)

    return Tokens.model_validate(tokens_raw)
