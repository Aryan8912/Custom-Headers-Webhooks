import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse, TenantListResponse
from app.exceptions import TenantNotFoundError
from app.cache import cache_get, cache_set, cache_delete

logger = logging.getLogger(__name__)

# ── Cache key helper ───────────────────────────────────
def _tenant_cache_key(tenant_id: str) -> str:
    return f"tenant:{tenant_id}"


# ── Create tenant ──────────────────────────────────────
async def create_tenant(
    db: AsyncSession,
    data: TenantCreate,
) -> TenantResponse:

    tenant = Tenant(
        id=str(uuid.uuid4()),
        tenant_id=data.tenant_id,
        name=data.name,
        agent_id=data.agent_id,
        api_key=data.api_key,
        forward_url=data.forward_url,
        forward_headers=data.forward_headers,
        is_active=True,
    )

    db.add(tenant)
    await db.flush()

    logger.info(f"Created tenant: {data.tenant_id}")
    return TenantResponse.model_validate(tenant)


# ── Get tenant by tenant_id ────────────────────────────
async def get_tenant(
    db: AsyncSession,
    tenant_id: str,
) -> TenantResponse:

    # check cache first
    cached = await cache_get(_tenant_cache_key(tenant_id))
    if cached:
        logger.debug(f"Cache hit for tenant: {tenant_id}")
        return TenantResponse(**cached)

    # fetch from DB
    result = await db.execute(
        select(Tenant).where(
            Tenant.tenant_id == tenant_id,
            Tenant.is_active == True,
        )
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise TenantNotFoundError(tenant_id)

    response = TenantResponse.model_validate(tenant)

    # store in cache for 5 min
    await cache_set(
        _tenant_cache_key(tenant_id),
        response.model_dump(mode="json"),
        ttl=300,
    )

    return response


# ── Get all tenants ────────────────────────────────────
async def get_all_tenants(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
) -> TenantListResponse:

    count_result = await db.execute(
        select(func.count()).where(Tenant.is_active == True)
    )
    total = count_result.scalar_one()

    result = await db.execute(
        select(Tenant)
        .where(Tenant.is_active == True)
        .order_by(Tenant.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    tenants = result.scalars().all()

    return TenantListResponse(
        total=total,
        items=[TenantResponse.model_validate(t) for t in tenants],
    )


# ── Update tenant ──────────────────────────────────────
async def update_tenant(
    db: AsyncSession,
    tenant_id: str,
    data: TenantUpdate,
) -> TenantResponse:

    result = await db.execute(
        select(Tenant).where(Tenant.tenant_id == tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise TenantNotFoundError(tenant_id)

    # only update fields that were passed
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(tenant, field, value)

    await db.flush()

    # invalidate cache
    await cache_delete(_tenant_cache_key(tenant_id))
    logger.info(f"Updated tenant: {tenant_id}")

    return TenantResponse.model_validate(tenant)


# ── Delete tenant (soft delete) ────────────────────────
async def delete_tenant(
    db: AsyncSession,
    tenant_id: str,
) -> dict:

    result = await db.execute(
        select(Tenant).where(Tenant.tenant_id == tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise TenantNotFoundError(tenant_id)

    tenant.is_active = False
    await db.flush()

    # invalidate cache
    await cache_delete(_tenant_cache_key(tenant_id))
    logger.info(f"Deleted tenant: {tenant_id}")

    return {"message": f"Tenant '{tenant_id}' deactivated successfully"}


# ── Verify tenant api_key ──────────────────────────────
async def verify_tenant_api_key(
    db: AsyncSession,
    tenant_id: str,
    api_key: str,
) -> bool:
    try:
        tenant = await get_tenant(db, tenant_id)
        return tenant.api_key == api_key
    except TenantNotFoundError:
        return False