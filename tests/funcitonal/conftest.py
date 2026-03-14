import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool, StaticPool
from src.main import app
from src.database import get_async_session
from src.auth.dependencies import current_optional_active_user, current_active_user
from src.models.base import Base
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
import src.redis
from src.auth.models import User
from src.auth.backend import auth_backend
import uuid
from src.models.links import Link
import datetime


TEST_DB_URL = "sqlite+aiosqlite:///./test.db"
engine_test = create_async_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    # poolclass=StaticPool,
)

TestSession = async_sessionmaker(
    engine_test,
    expire_on_commit=False,
    class_=AsyncSession,
)

async def override_get_async_session():
    async with TestSession() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session

@pytest_asyncio.fixture
async def db():
    async with TestSession() as session:
        yield session

@pytest_asyncio.fixture(scope="session")
async def event_loop():
    loop = asyncio.get_event_loop().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# # клиент без авторизации
# @pytest_asyncio.fixture
# async def async_client():
#     async with AsyncClient(app=app, base_url="http://test") as a_client:
#         yield a_client

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:
        yield client

# клиент с авторизацией
@pytest_asyncio.fixture
async def test_user():
    async with TestSession() as session:
        unique_email = f"test_{uuid.uuid4().hex[:8]}@test.com"
        user = User(
            email=unique_email,
            hashed_password="fakehashed",
            is_active=True,
            is_superuser=False,
            is_verified=True,
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user

@pytest_asyncio.fixture
async def auth_token(test_user):
    strategy = auth_backend.get_strategy()
    token = await strategy.write_token(test_user)

    return token

@pytest_asyncio.fixture
async def auth_client(async_client, auth_token):
    async_client.headers.update({
        "Authorization": f"Bearer {auth_token}"
    })

    return async_client

@pytest_asyncio.fixture
async def override_user(test_user):
    async def _override_user():
        return test_user
    app.dependency_overrides[current_optional_active_user] = _override_user
    yield
    app.dependency_overrides.pop(current_optional_active_user, None)

# мок редиса
@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    redis_mock = AsyncMock()

    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.delete.return_value = 1
    redis_mock.exists.return_value = 0

    monkeypatch.setattr("src.redis.redis", redis_mock)
    monkeypatch.setattr("src.routers.links.redis", redis_mock)


    return redis_mock

# создание ссылок
@pytest_asyncio.fixture
async def create_links(auth_client, db, test_user):
    links_data = [
        {"original_url": "https://example.com", "user_id": test_user.id},
        {"original_url": "https://example.org", "user_id": None},
        {"original_url": "https://example.net", "user_id": None},
    ]

    created_links = []
    for c, data in enumerate(links_data):
        link = Link(
            original_url=data["original_url"],
            short_code=f"code_{str(uuid.uuid4())[:8]}",
            created_at=datetime.datetime.utcnow(),
            user_id=data["user_id"],
            is_active=True,
        )
        db.add(link)
        created_links.append(link)
    await db.commit()
    for link in created_links:
        await db.refresh(link)

    return created_links