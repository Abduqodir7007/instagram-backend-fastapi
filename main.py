import events
from fastapi import FastAPI
from database import engine, Base
from endpoints import auth, post

app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(auth.routes)
app.include_router(post.routes)
