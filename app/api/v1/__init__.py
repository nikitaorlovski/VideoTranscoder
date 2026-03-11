from app.api.v1.auth import router as auth_router
from app.api.v1.video import router as video_router
from app.api.v1.task import router as task_router

__all__ = ["auth_router", "video_router", "task_router"]
