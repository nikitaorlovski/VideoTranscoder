import pytest
from app.services.video_service import VideoService


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


@pytest.mark.asyncio
async def test_convert_to_480_video_not_found(authorized_client):
    client, user = authorized_client

    response = await client.post(f"api/v1/videos/randomid/convert/480")
    assert response.status_code == 404, response.text


@pytest.mark.asyncio
async def test_convert_to_480_valid(authorized_client, video_factory, mocker):
    client, user = authorized_client
    video = await video_factory(owner_id=user.id)
    delay_mock = mocker.patch("app.api.v1.video.convert_to_480_task.delay")
    delay_mock.return_value.id = "fake-task-id"
    response = await client.post(f"/api/v1/videos/{video.uuid}/convert/480")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["video_id"] == video.uuid
    assert data["task_id"] == "fake-task-id"
    delay_mock.assert_called_once_with(video.uuid)


@pytest.mark.asyncio
async def test_get_thumbnail_video_not_found(authorized_client, mocker, tmp_path):
    client, user = authorized_client
    thumb_path = tmp_path / "thumb.jpg"
    thumb_path.write_bytes(b"fake-jpeg-data")

    get_thumbnail_mock = mocker.patch(
        "app.api.v1.video.VideoService.get_thumbnail",
        side_effect=ValueError("Video not found"),
    )
    response = await client.get(f"/api/v1/videos/123/thumbnail")

    assert response.status_code == 404
    get_thumbnail_mock.assert_called_once_with("123", user.id)


@pytest.mark.asyncio
async def test_get_thumbnail_source_not_found(authorized_client, mocker):
    client, user = authorized_client

    get_thumbnail_mock = mocker.patch(
        "app.api.v1.video.VideoService.get_thumbnail",
        side_effect=FileNotFoundError("Source video not found"),
    )

    response = await client.get("/api/v1/videos/randomid/thumbnail")

    assert response.status_code == 404
    assert response.json() == {"detail": "Source video not found"}
    get_thumbnail_mock.assert_called_once_with("randomid", user.id)


@pytest.mark.asyncio
async def test_get_thumbnail_valid(authorized_client, video_factory, mocker, tmp_path):
    client, user = authorized_client
    video = await video_factory(owner_id=user.id)
    thumb_path = tmp_path / "thumb.jpg"
    thumb_path.write_bytes(b"fake-jpeg-data")

    get_thumbnail_mock = mocker.patch(
        "app.api.v1.video.VideoService.get_thumbnail", return_value=thumb_path
    )
    response = await client.get(f"/api/v1/videos/{video.uuid}/thumbnail")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    get_thumbnail_mock.assert_called_once_with(video.uuid, user.id)


@pytest.mark.asyncio
async def test_get_thumbnail_ffmpeg_failed(authorized_client, mocker):
    client, user = authorized_client

    get_thumb_mock = mocker.patch(
        "app.api.v1.video.VideoService.get_thumbnail",
        side_effect=RuntimeError("ffmpeg error"),
    )

    response = await client.get("/api/v1/videos/randomid/thumbnail")

    assert response.status_code == 500
    assert response.json() == {"detail": "Thumbnail generation failed: ffmpeg error"}
    get_thumb_mock.assert_called_once_with("randomid", user.id)


@pytest.mark.asyncio
async def test_service_get_thumbnail_video_not_found(mocker):
    repo = mocker.Mock()
    repo.get_by_uuid_and_owner = mocker.AsyncMock(return_value=None)

    service = VideoService(repo)

    with pytest.raises(ValueError, match="Video not found"):
        await service.get_thumbnail("video123", 1)


@pytest.mark.asyncio
async def test_service_get_thumbnail_source_not_found(mocker):
    video = mocker.Mock()
    video.path = "/fake/path/video.mp4"

    repo = mocker.Mock()
    repo.get_by_uuid_and_owner = mocker.AsyncMock(return_value=video)

    service = VideoService(repo)

    mocker.patch("app.services.video_service.os.path.exists", return_value=False)

    with pytest.raises(FileNotFoundError, match="Source video not found"):
        await service.get_thumbnail("video123", 1)


@pytest.mark.asyncio
async def test_service_get_thumbnail_ffmpeg_failed(mocker, tmp_path):
    video = mocker.Mock()
    video.path = str(tmp_path / "video.mp4")

    repo = mocker.Mock()
    repo.get_by_uuid_and_owner = mocker.AsyncMock(return_value=video)

    service = VideoService(repo)

    mocker.patch("app.services.video_service.os.path.exists", return_value=True)

    fake_tmp = mocker.Mock()
    fake_tmp.name = str(tmp_path / "thumb.jpg")
    fake_tmp.close = mocker.Mock()

    mocker.patch(
        "app.services.video_service.tempfile.NamedTemporaryFile", return_value=fake_tmp
    )

    process = mocker.Mock()
    process.returncode = 1
    process.communicate = mocker.AsyncMock(return_value=(b"", b"ffmpeg failed"))

    mocker.patch(
        "app.services.video_service.asyncio.create_subprocess_exec",
        new=mocker.AsyncMock(return_value=process),
    )

    with pytest.raises(RuntimeError, match="ffmpeg failed"):
        await service.get_thumbnail("video123", 1)


@pytest.mark.asyncio
async def test_service_get_thumbnail_success(mocker, tmp_path):
    video = mocker.Mock()
    video.path = str(tmp_path / "video.mp4")

    repo = mocker.Mock()
    repo.get_by_uuid_and_owner = mocker.AsyncMock(return_value=video)

    service = VideoService(repo)

    mocker.patch("app.services.video_service.os.path.exists", return_value=True)

    fake_tmp = mocker.Mock()
    fake_tmp.name = str(tmp_path / "thumb.jpg")
    fake_tmp.close = mocker.Mock()

    mocker.patch(
        "app.services.video_service.tempfile.NamedTemporaryFile", return_value=fake_tmp
    )

    process = mocker.Mock()
    process.returncode = 0
    process.communicate = mocker.AsyncMock(return_value=(b"", b""))

    subprocess_mock = mocker.AsyncMock(return_value=process)
    mocker.patch(
        "app.services.video_service.asyncio.create_subprocess_exec",
        subprocess_mock,
    )

    result = await service.get_thumbnail("video123", 1)

    assert result == str(tmp_path / "thumb.jpg")
