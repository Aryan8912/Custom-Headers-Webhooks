import logging
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db_session, verify_bolna_headers
from app.schemas.webhook import BolnaWebhookPayload, WebhookAckResponse
from app.services.webhook_service import save_execution
from app.tasks import process_execution_task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["Webhook"])


# ── Main receiver ──────────────────────────────────────
# This URL goes into Bolna Analytics tab → webhook URL
# Bolna sends:
#   Authorization: Bearer <SECRET_KEY>
#   X-API-Key: <X_API_KEY>
#   X-Tenant-ID: <tenant_id>
@router.post(
    "/bolna",
    response_model=WebhookAckResponse,
    summary="Receive Bolna execution data webhook",
)
async def receive_bolna_webhook(
    payload: BolnaWebhookPayload,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
    headers: dict = Depends(verify_bolna_headers),
):
    tenant_id = headers["tenant_id"]

    # save to DB immediately
    log = await save_execution(
        db=db,
        payload=payload,
        tenant_id=tenant_id,
        auth_verified=True,
    )

    # enqueue background processing (forward, notify, etc.)
    background_tasks.add_task(
        process_execution_task,
        log_id=log.id,
        tenant_id=tenant_id,
        payload=payload.model_dump(),
    )

    logger.info(
        f"Webhook received: execution_id={payload.execution_id} "
        f"tenant={tenant_id} status={payload.status}"
    )

    # immediately return 200 to Bolna — never make Bolna wait
    return WebhookAckResponse(
        execution_id=payload.execution_id or payload.id or "unknown",
        status="queued",
        message="Webhook received and queued for processing",
    )