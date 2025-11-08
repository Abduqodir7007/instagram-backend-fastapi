import secrets
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from config import settings
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from fastapi_mail import MessageSchema, FastMail, ConnectionConfig
from models import User
from sqlalchemy.future import select
from google.oauth2 import id_token
from google.auth.transport import requests

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

pass_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain_pass: str, hashed_pass: str):
    return pass_context.verify(plain_pass, hashed_pass)


def hash_password(password: str):
    return pass_context.hash(password)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=settings.JWT_ALGORITHM
        )
        email: str = payload.get("email")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exists"
        )
    return user


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = int((datetime.utcnow() + timedelta(minutes=60)).timestamp())
    to_encode.update({"expire": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = int((datetime.utcnow() + timedelta(days=15)).timestamp())
    to_encode.update({"expire": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


async def send_verification_email(recipient_email: str, verification_code: str):

    if not conf:
        print("WARN: Email settings not configured. Skipping email sending.")
        return

    message_body = f"""
    <p>Hello,</p>
    <p>Thank you for registering! Please use this code to verify your account:</p>
    <h2 style="color: #333; text-align: center; background-color: #f0f0f0; padding: 10px; border-radius: 5px;">{verification_code}</h2>
    <br>
    <p>Best regards,</p>
    <p>STEAM Bridge</p>
    """

    message = MessageSchema(
        subject="Подтверждение регистрации",
        recipients=[recipient_email],
        body=message_body,
        subtype="html",
    )

    fm = FastMail(conf)
    await fm.send_message(message)


async def verify_google_id(google_id: str, db: AsyncSession):
    try:
        payload = id_token.verify_oauth2_token(
            google_id, requests.Request(), settings.CLIENT_ID
        )

        if payload and payload.get(email := "email"):
            email = payload.get("email")

        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()

        if not user:
            hashed_pw = hash_password(secrets.token_urlsafe(16))
            user = User(
                email=email,
                username=payload.get("name", email.split("@")[0]),
                password=hashed_pw,  # Google accounts are pre-verified
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        access_token = create_access_token({"sub": user.email})
        refresh_token = create_refresh_token({"sub": user.email})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    except ValueError as e:
        return f"Error: {e}"
