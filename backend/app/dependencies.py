from fastapi import Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db import get_db
from app.cache import get_redis
from app.config import get_settings
from app.exceptions import WebhookAuthError, TenantNotFoundError

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
# Bolna sends: Authorization: Bearer <SECRET_KEY>
async def verify_auth_header(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
):
    if credentials is None:
        raise WebhookAuthError("Missing Authorization header")

    if credentials.credentials != settings.SECRET_KEY:
        raise WebhookAuthError("Invalid Authorization token")

    return credentials.credentials


# ── Verify X-API-Key header ────────────────────────────
# Bolna sends: X-API-Key: <X_API_KEY>
async def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    if x_api_key is None:
        raise WebhookAuthError("Missing X-API-Key header")

    if x_api_key != settings.X_API_KEY:
        raise WebhookAuthError("Invalid X-API-Key")

    return x_api_key


# ── Extract and verify X-Tenant-ID header ─────────────
# Bolna sends: X-Tenant-ID: <tenant_id>
async def get_tenant_id(
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
) -> str:
    if x_tenant_id is None:
        raise TenantNotFoundError("missing")

    if x_tenant_id not in settings.tenant_list:
        raise TenantNotFoundError(x_tenant_id)

    return x_tenant_id


# ── Combined: verify all three headers at once ─────────
# Use this on the webhook receiver route
async def verify_bolna_headers(
    auth: str = Depends(verify_auth_header),
    api_key: str = Depends(verify_api_key),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    return {
        "auth": auth,
        "api_key": api_key,
        "tenant_id": tenant_id,
    }