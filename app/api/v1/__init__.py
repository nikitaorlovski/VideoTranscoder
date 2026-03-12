from app.api.v1.auth import router as auth_router
from app.api.v1.video import router as video_router
from app.api.v1.task import router as task_router

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)
router.include_router(video_router)
router.include_router(task_router)
