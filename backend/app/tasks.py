import logging
import httpx
from typing import Optional
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# ── Background task: process execution after save ──────
# Runs after webhook route returns 200 to Bolna
async def process_execution_task(
    log_id: str,
    tenant_id: str,
    payload: dict,
):
    logger.info(
        f"Processing execution: log_id={log_id} tenant={tenant_id}"
    )

    # import here to avoid circular imports
    from app.db import AsyncSessionLocal
    from app.services.webhook_service import mark_forwarded
    from app.services.tenant_service import get_tenant
    from app.exceptions import TenantNotFoundError

    async with AsyncSessionLocal() as db:
        try:
            # get tenant forward config
            tenant = await get_tenant(db, tenant_id)

            # forward to downstream if configured
            if tenant.forward_url:
                await _forward_to_downstream(
                    db=db,
                    log_id=log_id,
                    target_url=tenant.forward_url,
                    headers=tenant.forward_headers or {},
                    payload=payload,
                )
            else:
                logger.info(
                    f"No forward_url for tenant={tenant_id}, skipping forward"
                )

            await db.commit()

        except TenantNotFoundError:
            logger.error(f"Tenant not found during processing: {tenant_id}")
        except Exception as e:
            logger.error(f"Error processing execution {log_id}: {e}")
            await db.rollback()


# ── Forward payload to downstream URL ─────────────────
async def _forward_to_downstream(
    db,
    log_id: str,
    target_url: str,
    headers: dict,
    payload: dict,
):
    from app.services.webhook_service import mark_forwarded

    base_headers = {"Content-Type": "application/json"}
    all_headers = {**base_headers, **headers}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                target_url,
                json=payload,
                headers=all_headers,
            )
            response.raise_for_status()

            await mark_forwarded(db, log_id, response.status_code)
            logger.info(
                f"Forwarded to {target_url} — status={response.status_code}"
            )

    except httpx.HTTPStatusError as e:
        await mark_forwarded(
            db, log_id,
            e.response.status_code,
            error=str(e),
        )
        logger.error(f"Forward failed: {target_url} — {e}")

    except Exception as e:
        await mark_forwarded(db, log_id, 0, error=str(e))
        logger.error(f"Forward error: {target_url} — {e}")