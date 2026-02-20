from app.domain.exceptions import UserAlreadyExists
from app.models.users import UserOrm
from app.repositories.user_repository import UserRepository
from app.schemas.users import UserRegister, UserSchema
from app.core.security import hash_password, encode_jwt

from app.schemas.token import Token


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def register(self, user: UserRegister) -> Token:
        if exists_user := await self.repo.get_user_by_email(user.email):
            raise UserAlreadyExists()
        hashed_password = hash_password(user.password)
        new_user = await self.repo.register(
            UserOrm(
                username=user.username,
                email=user.email,
                password=hashed_password,
            )
        )
        payload = {"sub": str(new_user.id), "email": new_user.email}
        user_jwt = encode_jwt(payload)
        return Token(access_token=user_jwt, token_type="bearer")

    async def get_user_by_email(self, email: str) -> UserSchema | None:
        if not (user := await self.repo.get_user_by_email(email)):
            return None
        return UserSchema.model_validate(user)
