from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select
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

    async def get_all_user_videos(self, user_id) -> list[VideoOrm]:
        result = await self.session.execute(
            select(VideoOrm).where(VideoOrm.owner_id == user_id)
        )
        return result.scalars().all()
