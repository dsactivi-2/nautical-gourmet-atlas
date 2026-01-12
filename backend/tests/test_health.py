import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health endpoint returns ok status"""
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "service" in data
