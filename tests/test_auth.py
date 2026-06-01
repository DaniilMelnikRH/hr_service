import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "email": "newuser@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "securepass123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"

@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    response1 = await client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "first_name": "John",
        "last_name": "Doe",
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

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
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

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
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

@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, auth_token):
    if not auth_token:
        pytest.skip("Auth token not available")
    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"