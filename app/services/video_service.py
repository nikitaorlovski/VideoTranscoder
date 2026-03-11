from app.models.video import VideoOrm
from app.repositories.video_repository import VideoRepository
from app.schemas.videos import VideoMeta
import uuid
import os
import logging
import aiofiles
import asyncio

logger = logging.getLogger(__name__)


class VideoService:
    def __init__(self, repo: VideoRepository):
        self.repo = repo
        self.storage = "/app/storage/videos"

    def get_source_dir(self) -> str:
        return os.path.join(self.storage, "source")

    def get_480_dir(self) -> str:
        return os.path.join(self.storage, "480")

    def build_source_path(self, video_id: str, extension: str) -> str:
        extension = extension.lower()
        return os.path.join(self.get_source_dir(), f"{video_id}.{extension}")

    def build_480_path(self, video_id: str) -> str:
        return os.path.join(self.get_480_dir(), f"{video_id}_480.mp4")

    async def add_new_video(self, video_meta: VideoMeta, video_file):
        video_id = str(uuid.uuid4())
        file_path = self.build_source_path(video_id, video_meta.extension)

        new_video = await self.repo.add_new_video(
            VideoOrm(
                **video_meta.model_dump(),
                uuid=video_id,
                status="uploading",
                path=file_path,
            )
        )

        try:
            os.makedirs(self.get_source_dir(), exist_ok=True)

            async with aiofiles.open(file_path, "wb") as f:
                while True:
                    chunk = await video_file.read(1024 * 1024)
                    if not chunk:
                        break
                    await f.write(chunk)

            new_video.status = "uploaded"
            await self.repo.update(new_video)
            return new_video

        except Exception:
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

    async def convert_to_480(self, video_id: str) -> VideoOrm:
        video = await self.repo.get_by_uuid(video_id)
        if not video:
            raise ValueError(f"Video with id={video_id} not found")

        source_path = video.path
        converted_uuid = str(uuid.uuid4())
        output_path = self.build_480_path(converted_uuid)

        if not os.path.exists(source_path):
            video.status = "failed"
            await self.repo.update(video)
            raise FileNotFoundError(f"Source file not found: {source_path}")

        os.makedirs(self.get_480_dir(), exist_ok=True)

        video.status = "processing"
        await self.repo.update(video)

        try:
            process = await asyncio.create_subprocess_exec(
                "ffmpeg",
                "-y",
                "-i",
                source_path,
                "-vf",
                "scale=-2:480",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "23",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                output_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(
                    "ffmpeg failed for video_id=%s, stdout=%s, stderr=%s",
                    video_id,
                    stdout.decode(errors="ignore"),
                    stderr.decode(errors="ignore"),
                )
                video.status = "failed"
                await self.repo.update(video)
                raise RuntimeError("Video conversion failed")

            result_video = await self.repo.add_new_video(
                VideoOrm(
                    uuid=str(uuid.uuid4()),
                    filename=f"cropped_480_{video.filename}",
                    extension="mp4",
                    size=os.path.getsize(output_path),
                    status="ready",
                    owner_id=video.owner_id,
                    path=output_path,
                )
            )

            video.status = "ready"
            await self.repo.update(video)

            return result_video

        except Exception:
            logger.exception("Conversion to 480p failed for video_id=%s", video_id)

            video.status = "failed"
            await self.repo.update(video)

            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
            except Exception:
                logger.exception("Failed to remove converted file: %s", output_path)

            raise

    async def get_video_by_uuid_and_owner(
        self,
        video_id: str,
        owner_id: int,
    ) -> VideoOrm | None:
        return await self.repo.get_by_uuid_and_owner(video_id, owner_id)
