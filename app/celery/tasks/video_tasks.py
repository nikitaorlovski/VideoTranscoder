import asyncio

from app.celery.celery_app import app as celery_app
from app.repositories.video_repository import VideoRepository
from app.services.video_service import VideoService
from app.database.db import new_session
import logging

logger = logging.getLogger(__name__)


@celery_app.task(
    name="convert_to_480",
    bind=True,
    autoretry_for=(RuntimeError,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def convert_to_480_task(self, video_id: str):
    asyncio.run(with_video_service(_run_convert_to_480, video_id))


async def _run_convert_to_480(service: VideoService, video_id: str):
    logger.info(
        "Starting resolution conversion: video_id=%s",
        video_id,
    )
    await service.convert_to_480(video_id)


@celery_app.task(
    name="convert_video_format",
    bind=True,
    autoretry_for=(RuntimeError,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def convert_video_format_task(self, video_id: str, target_format: str):
    logger.info(
        "Starting format conversion: video_id=%s target_format=%s",
        video_id,
        target_format,
    )
    asyncio.run(with_video_service(_run_convert_video_format, video_id, target_format))


async def _run_convert_video_format(
    service: VideoService,
    video_id: str,
    target_format: str,
):
    await service.convert_video_format(video_id, target_format)


async def with_video_service(callback, *args):
    async with new_session() as session:
        repo = VideoRepository(session)
        service = VideoService(repo)
        return await callback(service, *args)
