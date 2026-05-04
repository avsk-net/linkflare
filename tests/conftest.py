import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.database import Base, get_db
from app.dependencies import get_redis

TEST_DB_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DB_URL)
TestSession = async_sessionmaker(test_engine, expire_on_commit=False)


async def override_get_db():
    async with TestSession() as session:
        yield session


async def override_get_redis():
    return None  # disables rate limiting in tests


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_redis] = override_get_redis


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_client(client):
    await client.post("/auth/register", json={"email": "test@example.com", "password": "testpass123"})
    resp = await client.post("/auth/login", json={"email": "test@example.com", "password": "testpass123"})
    token = resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client
