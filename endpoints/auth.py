from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from routes.user import UserRegister, UserLogin, UserPublic, VerifyUser, Token
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import User
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import UUID

from security import (
    get_current_user,
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    send_verification_email,
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
    print("new user:", new_user)

    db.add(new_user)
    await db.commit()
    verification_code = new_user.generate_code(db)
    background_tasks.add_task(send_verification_email, user_in.email, verification_code)

    access_token = create_access_token({"email": user_in.email})
    refresh_token = create_refresh_token({"email": user_in.email})

    return {"access_token": access_token, "refresh_token": refresh_token}


@routes.get("/")
async def get_all_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@routes.delete("/users/{user_id}")
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.id==user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()

    return {"message": "User deleted successfully"}
