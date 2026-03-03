import uvicorn
from redis import Redis
from fastapi import FastAPI
from app.api.v1 import auth_router, video_router
from contextlib import asynccontextmanager

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis(
        host=settings.redis.host, port=settings.redis.port, db=settings.redis.db
    )
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(video_router)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
