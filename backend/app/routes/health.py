import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.dependencies import get_db_session
from app.cache import get_redis
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/health", tags=["Health"])


# ── Basic health check ─────────────────────────────────
@router.get(
    "",
    summary="Basic health check",
)
async def health():
    return {
        "status": "ok",
        "env": settings.APP_ENV,
    }


# ── Deep health check ──────────────────────────────────
# Checks DB and Redis connectivity
@router.get(
    "/deep",
    summary="Deep health check — DB and Redis",
)
async def deep_health(
    db: AsyncSession = Depends(get_db_session),
):
    result = {"status": "ok", "checks": {}}

    # ── Check DB ───────────────────────────────────────
    try:
        await db.execute(text("SELECT 1"))
        result["checks"]["database"] = "ok"
    except Exception as e:
        result["checks"]["database"] = f"error: {str(e)}"
        result["status"] = "degraded"

    # ── Check Redis ────────────────────────────────────
    try:
        redis = await get_redis()
        await redis.ping()
        result["checks"]["redis"] = "ok"
    except Exception as e:
        result["checks"]["redis"] = f"error: {str(e)}"
        result["status"] = "degraded"

    return result