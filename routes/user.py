from pydantic import BaseModel, EmailStr
from sqlalchemy.dialects.postgresql import UUID


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublin(BaseModel):
    id: UUID
    email: EmailStr

class VerifyUser:
    code: str