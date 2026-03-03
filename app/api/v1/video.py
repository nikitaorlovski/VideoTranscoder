from fastapi import APIRouter, UploadFile, Depends

from app.dependencies import get_video_service, get_current_auth_user
from app.schemas.users import UserSchema
from app.schemas.videos import VideoMeta
from app.services.video_service import VideoService

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
