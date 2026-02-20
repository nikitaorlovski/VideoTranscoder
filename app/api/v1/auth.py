from fastapi import APIRouter
from app.schemas import UserRegister

router = APIRouter()

@router.post("/register")
async def registration(user: UserRegister):
    return {"message" : "User has been registered"}