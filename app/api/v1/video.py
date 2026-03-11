from fastapi import APIRouter, UploadFile, Depends, HTTPException, status

from app.dependencies import get_video_service, get_current_auth_user
from app.schemas.users import UserSchema
from app.schemas.videos import VideoMeta, VideoConvertResponse
from app.services.video_service import VideoService
from app.celery.tasks.video_tasks import convert_to_480_task

router = APIRouter(prefix="/api/v1/videos", tags=["VideoAPI"])


@router.post("/")
async def upload_video(
    video: UploadFile,
    service: VideoService = Depends(get_video_service),
    user: UserSchema = Depends(get_current_auth_user),
):
    new_video = VideoMeta(
        owner_id=user.id,
        filename=video.filename,
        extension=video.filename.split(".")[-1],
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
