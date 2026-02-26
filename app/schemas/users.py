from pydantic import BaseModel, EmailStr, ConfigDict


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserSchema(BaseModel):
    id: int
    email: EmailStr
    username: str
    password: bytes
    is_admin: bool
    model_config = ConfigDict(from_attributes=True)
