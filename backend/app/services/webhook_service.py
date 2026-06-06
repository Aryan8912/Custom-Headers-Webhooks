import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.models.execution_log import ExecutionLog
from app.schemas.webhook import BolnaWebhookPayload, ExecutionLogResponse, ExecutionLogListResponse
from app.exceptions import ExecutionNotFoundError

logger = logging.getLogger(__name__)


# ── Save incoming Bolna webhook to DB ──────────────────
async def save_execution(
    db: AsyncSession,
    payload: BolnaWebhookPayload,
    tenant_id: str,
    auth_verified: bool = True,
) -> ExecutionLog:

    log = ExecutionLog(
        id=str(uuid.uuid4()),
        execution_id=payload.execution_id,
        agent_id=payload.agent_id,
        tenant_id=tenant_id,
        status=payload.status,
        payload=payload.model_dump(mode="json"),
        auth_verified=auth_verified,
        forwarded=False,
    )
    db.add(log)
    await db.flush()
    await db.commit()
    await db.refresh(log)

    logger.info(
        f"Saved execution: execution_id={payload.execution_id} "
        f"tenant={tenant_id} status={payload.status}"
    )

    return log


# ── Mark execution as forwarded ────────────────────────
async def mark_forwarded(
    db: AsyncSession,
    log_id: str,
    status_code: int,
    error: Optional[str] = None,
) -> ExecutionLog:

    result = await db.execute(
        select(ExecutionLog).where(ExecutionLog.id == log_id)
    )
    log = result.scalar_one_or_none()

    if not log:
        raise ExecutionNotFoundError(log_id)

    log.forwarded = error is None
    log.forward_status_code = status_code
    log.forward_error = error

    await db.flush()
    return log


# ── Get single execution by execution_id ──────────────
async def get_execution(
    db: AsyncSession,
    execution_id: str,
    tenant_id: str,
) -> ExecutionLogResponse:

    result = await db.execute(
        select(ExecutionLog).where(
            ExecutionLog.execution_id == execution_id,
            ExecutionLog.tenant_id == tenant_id,
        )
    )
    log = result.scalar_one_or_none()

    if not log:
        raise ExecutionNotFoundError(execution_id)

    return ExecutionLogResponse.model_validate(log)


# ── Get paginated execution logs ───────────────────────
async def get_executions(
    db: AsyncSession,
    tenant_id: str,
    agent_id: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> ExecutionLogListResponse:

    # base query filtered by tenant
    query = select(ExecutionLog).where(
        ExecutionLog.tenant_id == tenant_id
    )

    # optional filters
    if agent_id:
        query = query.where(ExecutionLog.agent_id == agent_id)
    if status:
        query = query.where(ExecutionLog.status == status)

    # total count
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar_one()

    # paginate
    query = query.order_by(ExecutionLog.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    logs = result.scalars().all()

    return ExecutionLogListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[ExecutionLogResponse.model_validate(log) for log in logs],
    )