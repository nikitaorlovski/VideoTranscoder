from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from app.models.users import UserOrm


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register(self, user: UserOrm) -> UserOrm:
        self.session.add(user)
        await self.session.commit()
        return user

    async def get_user_by_email(self, email: str) -> UserOrm | None:
        result = await self.session.execute(
            select(UserOrm).where(UserOrm.email == email)
        )
        return result.scalars().first()
