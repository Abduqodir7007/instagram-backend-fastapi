from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from routes.user import UserRegister, UserLogin, UserPublic, VerifyUser, Token
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import User, VerifyUsers
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import UUID
from security import oauth2_scheme
from datetime import datetime
from security import (
    get_current_user,
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    send_verification_email,
    send_email,
)


routes = APIRouter(prefix="/auth")


@routes.post("/register", status_code=status.HTTP_201_CREATED)
async def register_new_user(
    user_in: UserRegister,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(select(User).where(User.email == user_in.email))

    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )

    new_user = User(
        username=user_in.username,
        email=user_in.email,
        password=hash_password(user_in.password),
    )

    db.add(new_user)
    await db.commit()
    verification_code = await new_user.generate_code(db)
    background_tasks.add_task(send_verification_email, user_in.email, verification_code)

    # Printing code to the console during the development
    print(f"Your code is: {verification_code}")
    access_token = create_access_token({"email": user_in.email})
    refresh_token = create_refresh_token({"email": user_in.email})

    return {"access_token": access_token, "refresh_token": refresh_token}


@routes.post("/verify", status_code=status.HTTP_200_OK)
async def verify_email_code(
    verification_data: VerifyUser,
    token: str = Depends(oauth2_scheme),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(VerifyUsers).where(
            VerifyUsers.user_id == user.id,
            VerifyUsers.expiration_time >= datetime.utcnow(),
            VerifyUsers.is_verifyied == False,
            VerifyUsers.code == verification_data.code,
        )
    )
    code = result.scalars().first()
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong verification code"
        )
    code.is_verifyied = True

    await db.commit()
    await db.refresh(code)

    access_token = create_access_token({"email": user.email})
    refresh_token = create_refresh_token({"email": user.email})

    return {"access_token": access_token, "refresh_token": refresh_token}


@routes.get("/verify/all/")
async def get_all_verify(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VerifyUsers))
    res = result.scalars().all()
    return res


@routes.post("/login", status_code=status.HTTP_200_OK)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalars().first()

    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exists"
        )

    access_token = create_access_token({"email": user.email})
    refresh_token = create_refresh_token({"email": user.email})

    return {"access_token": access_token, "refresh_token": refresh_token}


@routes.get("/")
async def get_all_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@routes.delete("/users/{user_id}")
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()

    return {"message": "User deleted successfully"}
