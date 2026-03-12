from fastapi import UploadFile, HTTPException
from starlette import status
from app.core.config import settings

ALLOWED_VIDEO_EXTENSIONS = {"mp4", "mov", "mkv", "avi", "webm"}
ALLOWED_VIDEO_CONTENT_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/x-matroska",
    "video/x-msvideo",
    "video/webm",
}


def validate_video_upload(video: UploadFile) -> str:

    if "." not in video.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have an extension",
        )

    extension = video.filename.rsplit(".", 1)[-1].lower()

    if extension not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only video files are allowed",
        )
    if video.size > settings.video.max_size * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="File too large",
        )
    if video.content_type not in ALLOWED_VIDEO_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only video files are allowed",
        )

    return extension
