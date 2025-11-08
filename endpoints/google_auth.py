from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from authlib.integrations.starlette_client import OAuth
from config import settings
from sqlalchemy.future import select
import secrets
from security import (
    verify_google_id,
)

routes = APIRouter(prefix="/google")

oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.CLIENT_ID,
    client_secret=settings.CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@routes.get("/login")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_auth_callback")
    response = await oauth.google.authorize_redirect(request, redirect_uri)
    return response


@routes.get("/auth")
async def google_auth_callback(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)

        return await verify_google_id(token.get("id_token"), db)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}",
        )
