from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.core.auth import get_current_user, TokenClaims

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: str
    oidc_configured: bool
    demo_mode: bool


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.environment,
        database=db_status,
        oidc_configured=bool(settings.oidc_issuer_url and settings.oidc_client_id),
        demo_mode=settings.effective_demo_mode,
    )


class AuthTestResponse(BaseModel):
    authenticated: bool
    user_id: Optional[str] = None
    email: Optional[str] = None
    roles: list[str] = []


@router.get("/auth/test", response_model=AuthTestResponse)
async def auth_test(user: TokenClaims = Depends(get_current_user)):
    return AuthTestResponse(
        authenticated=True,
        user_id=user.sub,
        email=user.email,
        roles=user.roles,
    )