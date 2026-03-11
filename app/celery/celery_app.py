from celery import Celery

from app.core.config import settings

app = Celery(broker=settings.redis.url, backend=settings.redis.url)
app.conf.imports = ("app.celery.tasks.video_tasks",)
