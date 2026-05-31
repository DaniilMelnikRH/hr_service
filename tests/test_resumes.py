import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_resume(client, auth_headers):
    response = await client.get("/resumes/", headers=auth_headers)
    assert response.status_code == 200