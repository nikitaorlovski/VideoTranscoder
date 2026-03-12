import pytest


@pytest.mark.asyncio
async def test_get_videos_unauth(client):
    response = await client.get("/api/v1/videos/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_videos(authorized_client):
    client, user = authorized_client
    response = await client.get("/api/v1/videos/")
    data = response.json()
    assert response.status_code == 200
    assert data == []
