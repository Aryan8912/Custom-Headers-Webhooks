from fastapi import Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.db import get_db
from app.cache import get_redis, cache_get, cache_set
from app.config import get_settings
from app.exceptions import WebhookAuthError, TenantNotFoundError
from app.models.tenant import Tenant

settings = get_settings()
bearer_scheme = HTTPBearer(auto_error=False)


# ── DB session ─────────────────────────────────────────
async def get_db_session(
    db: AsyncSession = Depends(get_db),
) -> AsyncSession:
    return db


# ── Redis client ───────────────────────────────────────
async def get_redis_client():
    return await get_redis()


# ── Verify Authorization header ────────────────────────
async def verify_auth_header(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
):
    if credentials is None:
        raise WebhookAuthError("Missing Authorization header")
    if credentials.credentials != settings.SECRET_KEY:
        raise WebhookAuthError("Invalid Authorization token")
    return credentials.credentials


# ── Extract tenant ID from header ──────────────────────
# Used by executions route for read endpoints
async def get_tenant_id(
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
) -> str:
    if x_tenant_id is None:
        raise TenantNotFoundError("missing")
    if x_tenant_id not in settings.tenant_list:
        raise TenantNotFoundError(x_tenant_id)
    return x_tenant_id


# ── Cross-verify X-API-Key belongs to X-Tenant-ID ─────
async def verify_api_key_for_tenant(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
    db: AsyncSession = Depends(get_db),
) -> dict:

    if x_api_key is None:
        raise WebhookAuthError("Missing X-API-Key header")
    if x_tenant_id is None:
        raise TenantNotFoundError("missing")
    if x_tenant_id not in settings.tenant_list:
        raise TenantNotFoundError(x_tenant_id)

    # check cache first
    cache_key = f"tenant_apikey:{x_tenant_id}"
    cached_key = await cache_get(cache_key)

    if cached_key:
        if x_api_key != cached_key:
            raise WebhookAuthError(
                f"X-API-Key does not match tenant '{x_tenant_id}'"
            )
        return {"api_key": x_api_key, "tenant_id": x_tenant_id}

    # fallback: check DB
    result = await db.execute(
        select(Tenant).where(
            Tenant.tenant_id == x_tenant_id,
            Tenant.is_active == True,
        )
    )
    tenant = result.scalar_one_or_none()

    if tenant:
        await cache_set(cache_key, tenant.api_key, ttl=300)
        if x_api_key != tenant.api_key:
            raise WebhookAuthError(
                f"X-API-Key does not match tenant '{x_tenant_id}'"
            )
    else:
        if x_api_key != settings.X_API_KEY:
            raise WebhookAuthError(
                f"X-API-Key does not match tenant '{x_tenant_id}'"
            )

    return {"api_key": x_api_key, "tenant_id": x_tenant_id}


# ── Combined: verify all headers + cross-verify ────────
async def verify_bolna_headers(
    auth: str = Depends(verify_auth_header),
    tenant_data: dict = Depends(verify_api_key_for_tenant),
) -> dict:
    return {
        "auth": auth,
        "api_key": tenant_data["api_key"],
        "tenant_id": tenant_data["tenant_id"],
    }