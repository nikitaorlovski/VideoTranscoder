from app.models.video import VideoOrm
from app.repositories.video_repository import VideoRepository
from app.schemas.videos import VideoMeta
import uuid
import os
import logging
import aiofiles

logger = logging.getLogger(__name__)


class VideoService:
    def __init__(self, repo: VideoRepository):
        self.repo = repo
        self.storage = "storage/videos"

    async def add_new_video(self, video_meta: VideoMeta, video_file):
        video_id = str(uuid.uuid4())
        file_path = os.path.join(self.storage, f"{video_id}.{video_meta.extension}")
        new_video = await self.repo.add_new_video(
            VideoOrm(**video_meta.model_dump(), uuid=video_id, status="uploading")
        )
        try:
            os.makedirs(self.storage, exist_ok=True)
            async with aiofiles.open(file_path, "wb") as f:
                while True:
                    chunk = await video_file.read(1024 * 1024)
                    if not chunk:
                        break
                    await f.write(chunk)
                new_video.status = "ready"
                await self.repo.update(new_video)
        except Exception as e:
            logger.exception(
                "Video upload failed: video_id=%s path=%s owner_id=%s",
                video_id,
                file_path,
                new_video.owner_id,
            )

            new_video.status = "failed"
            await self.repo.update(new_video)

            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                logger.exception("Failed to remove file: %s", file_path)

            raise

    async def get_all_user_videos(self, user_id) -> list[VideoOrm]:
        return await self.repo.get_all_user_videos(user_id)
