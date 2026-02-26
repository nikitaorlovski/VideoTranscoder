from fastapi import APIRouter, Depends, HTTPException

from app.core.security import encode_jwt
from app.dependencies import (
    validate_current_user,
    get_user_service,
)
from app.domain.exceptions import UserAlreadyExists
from app.schemas import UserRegister
from app.schemas.token import Token
from app.schemas.users import UserSchema
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register")
async def registration(
    user: UserRegister, service: UserService = Depends(get_user_service)
):
    try:
        return await service.register(user)
    except UserAlreadyExists:
        raise HTTPException(status_code=409, detail="User already exists")


@router.post("/login")
async def login(user: UserSchema = Depends(validate_current_user)):
    jwt_payload = {"sub": str(user.id), "email": user.email}
    jwt = encode_jwt(jwt_payload)
    return Token(access_token=jwt, token_type="bearer")
