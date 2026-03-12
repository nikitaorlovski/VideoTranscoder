from app.validators.video_validator import validate_video_upload
from app.dependencies import get_video_service, get_current_auth_user
from app.schemas.users import UserSchema
from app.schemas.videos import VideoMeta, VideoConvertResponse
from app.services.video_service import VideoService
from app.celery.tasks.video_tasks import convert_to_480_task
from fastapi import (
    BackgroundTasks,
    Depends,
    HTTPException,
    APIRouter,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
import os

router = APIRouter(prefix="/videos", tags=["VideoAPI"])


@router.post("/")
async def upload_video(
    video: UploadFile,
    service: VideoService = Depends(get_video_service),
    user: UserSchema = Depends(get_current_auth_user),
):

    extension = validate_video_upload(video)
    new_video = VideoMeta(
        owner_id=user.id,
        filename=video.filename,
        extension=extension,
        size=video.size,
    )
    return await service.add_new_video(new_video, video)


@router.get("/")
async def get_videos(
    user: UserSchema = Depends(get_current_auth_user),
    service: VideoService = Depends(get_video_service),
):
    return await service.get_all_user_videos(user.id)


@router.post("/{video_id}/convert/480", response_model=VideoConvertResponse)
async def convert_video_to_480(
    video_id: str,
    service: VideoService = Depends(get_video_service),
    user: UserSchema = Depends(get_current_auth_user),
):
    video = await service.get_video_by_uuid_and_owner(video_id, user.id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    task = convert_to_480_task.delay(video.uuid)

    return VideoConvertResponse(
        video_id=video.uuid,
        task_id=task.id,
        status="processing",
    )


@router.get("/videos/{video_id}/thumbnail")
async def get_thumbnail(
    video_id: str,
    background_tasks: BackgroundTasks,
    service: VideoService = Depends(get_video_service),
    user: UserSchema = Depends(get_current_auth_user),
):
    try:
        thumbnail_path = await service.get_thumbnail(video_id, user.id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Video not found")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Source video not found")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Thumbnail generation failed: {e}")

    background_tasks.add_task(os.remove, thumbnail_path)

    return FileResponse(
        path=thumbnail_path,
        media_type="image/jpeg",
        filename=f"thumbnail.jpg",
    )
