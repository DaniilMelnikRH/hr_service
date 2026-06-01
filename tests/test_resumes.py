import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_resume(client, auth_headers):
    if not auth_headers:
        pytest.skip("Auth required")
    
    response = await client.post("/resumes/", headers=auth_headers, json={
        "candidate_name": "Test Candidate",
        "candidate_email": "candidate@example.com",
        "candidate_phone": "+79991234567",
        "skills": "Python, FastAPI",
        "experience_years": 3
    })
    assert response.status_code == 201
    data = response.json()
    assert data["candidate_name"] == "Test Candidate"
    assert "id" in data