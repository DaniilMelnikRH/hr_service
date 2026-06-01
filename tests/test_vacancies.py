import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_vacancies(client, auth_headers):
    response = await client.get("/vacancies/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_vacancy_not_found(client, auth_headers):
    response = await client.get("/vacancies/99999", headers=auth_headers)
    assert response.status_code == 404