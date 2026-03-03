from app.celery.celery_app import app as celery_app
from app.schemas.videos import Video


@celery_app.task(name="save_video")
async def save_video(video: Video):
    pass
    # TODO
    # Делать через сервисы и т.д как ранее
