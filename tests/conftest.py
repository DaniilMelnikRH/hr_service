import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.main import app
from app.database import get_db, Base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/hr_db")
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

@pytest_asyncio.fixture(autouse=True)
async def clean_tables():
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE vacancy_resumes RESTART IDENTITY CASCADE"))
        await conn.execute(text("TRUNCATE TABLE vacancies RESTART IDENTITY CASCADE"))
        await conn.execute(text("TRUNCATE TABLE resumes RESTART IDENTITY CASCADE"))
        await conn.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
        await conn.execute(text("TRUNCATE TABLE categories RESTART IDENTITY CASCADE"))
        await conn.execute(text("TRUNCATE TABLE positions RESTART IDENTITY CASCADE"))
    yield

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def auth_token(client):
    response = await client.post("/auth/register", json={
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "testpass123"
    })
    if response.status_code != 201:
        return None
    login_response = await client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    if login_response.status_code != 200:
        return None
    data = login_response.json()
    return data.get("access_token")

@pytest_asyncio.fixture
async def auth_headers(auth_token):
    if auth_token:
        return {"Authorization": f"Bearer {auth_token}"}
    return {}