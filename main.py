import events
from fastapi import FastAPI
from database import engine, Base
from endpoints import auth, post, google_auth, comments
from starlette.middleware.sessions import SessionMiddleware
from config import settings
import secrets

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(auth.routes)
app.include_router(post.routes)
app.include_router(google_auth.routes)
app.include_router(comments.    routes)


@app.get("/")
async def start():
    return {"message": "Api is running"}
