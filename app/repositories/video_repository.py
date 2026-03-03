from sqlalchemy.ext.asyncio.session import AsyncSession

from app.models.video import VideoOrm


class VideoRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_new_video(self, video: VideoOrm) -> VideoOrm:
        self.session.add(video)
        await self.session.commit()
        return video

    async def update(self, video: VideoOrm):
        await self.session.commit()
        return video
