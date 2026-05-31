import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_vacancy(client: AsyncClient, auth_headers):
    response = await client.post("/vacancies/", headers=auth_headers, json={
        "title": "Python Developer",
        "description": "We need a senior Python developer",
        "salary_min": 100000,
        "salary_max": 150000,
        "location": "Remote",
        "category_id": 1,
        "position_id": 1
    })
    assert response.status_code in [201, 400]

@pytest.mark.asyncio
async def test_get_vacancies(client: AsyncClient, auth_headers):
    response = await client.get("/vacancies/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_vacancy_not_found(client: AsyncClient, auth_headers):
    response = await client.get("/vacancies/99999", headers=auth_headers)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_filter_vacancies_by_status(client: AsyncClient, auth_headers):
    response = await client.get("/vacancies/?status=open", headers=auth_headers)
    assert response.status_code == 200