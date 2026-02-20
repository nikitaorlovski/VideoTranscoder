from typing import AsyncGenerator, Any
from jwt.exceptions import InvalidTokenError
from fastapi import Form, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password, decode_jwt
from app.database.db import new_session
from app.repositories.user_repository import UserRepository
from app.schemas.users import UserSchema
from app.services.user_service import UserService

http_bearer = HTTPBearer()


async def get_async_session() -> AsyncGenerator[AsyncSession | Any, Any]:
    async with new_session() as session:
        yield session


async def get_user_repository(
    session: AsyncSession = Depends(get_async_session),
) -> UserRepository:
    return UserRepository(session)


async def get_user_service(repo: UserRepository = Depends(get_user_repository)):
    return UserService(repo)


async def validate_current_user(
    email: EmailStr = Form(...),
    password: str = Form(...),
    service: UserService = Depends(get_user_service),
) -> UserSchema:
    unauth_exc = HTTPException(status_code=401, detail="Invalid email or password")
    if not (user := await service.get_user_by_email(email)):
        raise unauth_exc
    if not verify_password(password, user.password):
        raise unauth_exc
    return user


async def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
):
    token = credentials.credentials
    try:
        payload = decode_jwt(token)
    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token {e}")
    return payload


async def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
    service: UserService = Depends(get_user_service),
) -> UserSchema:
    if not (user := await service.get_user_by_email(payload["email"])):
        raise HTTPException(status_code=401, detail="Token invalid")
    return user
