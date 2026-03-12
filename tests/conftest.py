import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from httpx import ASGITransport, AsyncClient
import pytest
from app.core.config import settings
from app.core.security import hash_password
from app.database.db import Base
from app.dependencies import get_async_session
from app.models import UserOrm
from main import app

test_db_url = "sqlite+aiosqlite:///./test.db"
test_engine = create_async_engine(test_db_url)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_connection():
    async with test_engine.connect() as connection:
        transaction = await connection.begin()
        try:
            yield connection
        finally:
            await transaction.rollback()


@pytest_asyncio.fixture
async def test_db_session(db_connection):
    session = AsyncSession(bind=db_connection, expire_on_commit=False)
    try:
        yield session
    finally:
        await session.close()


@pytest_asyncio.fixture
async def client(test_db_session):
    async def override_get_session():
        yield test_db_session

    app.dependency_overrides[get_async_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://localhost",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user_factory(test_db_session):
    async def create_user(
        email: str = "test@example.com",
        password: str = "testpassword",
        username: str = "testusername",
    ):
        user = UserOrm(email=email, password=hash_password(password), username=username)
        db = test_db_session
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    return create_user


@pytest_asyncio.fixture
async def authorized_client(client, user_factory):
    user = await user_factory(email="authuser@example.com", password="authpass123")
    response = await client.post(
        "/api/v1/auth/login", data={"email": user.email, "password": "authpass123"}
    )
    access_token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    return client, user


@pytest.fixture
def small_video_limit():
    old_value = settings.video.max_size
    settings.video.max_size = 5  # 5 MB
    yield
    settings.video.max_size = old_value
