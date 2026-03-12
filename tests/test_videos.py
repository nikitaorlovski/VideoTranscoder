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


@pytest.mark.asyncio
async def test_upload_video_integration(authorized_client):
    client, user = authorized_client

    response = await client.post(
        "/api/v1/videos/",
        files={"video": ("video.mp4", b"fake video bytes", "video/mp4")},
    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["filename"] == "video.mp4"


@pytest.mark.parametrize(
    "filename, size, mime",
    [
        pytest.param("video", 5 * 1024 * 1024, "video/mp4", id="invalid filename"),
        pytest.param(
            "video.mp23", 5 * 1024 * 1024, "video/mp4", id="invalid extension"
        ),
        pytest.param("video.mp4", 5 * 1024 * 1024, "video/mp1", id="invalid mime-type"),
    ],
)
@pytest.mark.asyncio
async def test_upload_invalid_video(filename, size, mime, authorized_client):
    client, user = authorized_client
    content = b"x" * size
    response = await client.post(
        "/api/v1/videos/",
        files={"video": (filename, content, mime)},
    )
    print(response.text)
    assert response.status_code == 400, response.text


@pytest.mark.parametrize(
    "filename, size",
    [
        pytest.param("video.mp4", 6 * 1024 * 1024, id="invalid size"),
    ],
)
@pytest.mark.asyncio
async def test_upload_large_video(filename, size, authorized_client, small_video_limit):
    client, user = authorized_client
    content = b"x" * size
    response = await client.post(
        "/api/v1/videos/",
        files={"video": (filename, content, "video/mp4")},
    )
    print(response.text)
    assert response.status_code == 413, response.text
