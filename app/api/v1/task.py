from fastapi import APIRouter
from celery.result import AsyncResult

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/{task_id}")
async def get_task_status(task_id: str):

    task_result = AsyncResult(task_id)

    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.successful() else None,
    }
