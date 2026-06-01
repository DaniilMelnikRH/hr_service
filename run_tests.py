import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from app.main import app
from app.database import get_db, Base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/hr_db")
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

async def test_register_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/auth/register", json={
            "email": "newuser@example.com",
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "password": "securepass123"
        })
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()
        assert data["email"] == "newuser@example.com"
        print("test_register_success PASSED")

async def test_register_duplicate_email():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response1 = await client.post("/auth/register", json={
            "email": "duplicate@example.com",
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "password": "pass123"
        })
        assert response1.status_code == 201
        
        response2 = await client.post("/auth/register", json={
            "email": "duplicate@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "password": "pass456"
        })
        assert response2.status_code == 400
        assert "already registered" in response2.text
        print("test_register_duplicate_email PASSED")

async def test_login_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/auth/register", json={
            "email": "login@example.com",
            "first_name": "Login",
            "last_name": "Test",
            "password": "mypassword"
        })
        response = await client.post("/auth/login", json={
            "email": "login@example.com",
            "password": "mypassword"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
        print("test_login_success PASSED")

async def test_login_wrong_password():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/auth/register", json={
            "email": "wrongpass@example.com",
            "first_name": "Wrong",
            "last_name": "Pass",
            "password": "correctpass"
        })
        response = await client.post("/auth/login", json={
            "email": "wrongpass@example.com",
            "password": "wrongpass"
        })
        assert response.status_code == 401
        print("test_login_wrong_password PASSED")

async def test_get_me():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/auth/register", json={
            "email": "me@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpass123"
        })
        login_response = await client.post("/auth/login", json={
            "email": "me@example.com",
            "password": "testpass123"
        })
        token = login_response.json().get("access_token")
        
        response = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@example.com"
        print("test_get_me PASSED")

async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created")

async def cleanup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("Database tables dropped")

async def run_all_tests():
    print("\n" + "="*60)
    print("RUNNING TESTS")
    print("="*60 + "\n")
    
    await setup_db()
    
    tests = [
        test_register_success,
        test_register_duplicate_email,
        test_login_success,
        test_login_wrong_password,
        test_get_me,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test()
            passed += 1
        except AssertionError as e:
            print(f"{test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"{test.__name__} ERROR: {e}")
            failed += 1
    
    await cleanup_db()
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)