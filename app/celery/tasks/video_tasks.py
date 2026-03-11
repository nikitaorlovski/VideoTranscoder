import asyncio

from app.celery.celery_app import app as celery_app
from app.repositories.video_repository import VideoRepository
from app.services.video_service import VideoService
from app.database.db import new_session


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
    asyncio.run(_convert_to_480(video_id))


async def _convert_to_480(video_id: str):

    async with new_session() as session:
        repo = VideoRepository(session)
        service = VideoService(repo)
        await service.convert_to_480(video_id)
