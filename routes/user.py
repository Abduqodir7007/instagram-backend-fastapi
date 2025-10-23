from pydantic import BaseModel, EmailStr
from sqlalchemy.dialects.postgresql import UUID


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: str
    email: EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str


class VerifyUser(BaseModel):
    code: str
