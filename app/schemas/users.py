from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=5, max_length=20)


class UserSchema(BaseModel):
    id: int
    email: EmailStr
    username: str
    password: bytes
    is_admin: bool
    model_config = ConfigDict(from_attributes=True)
