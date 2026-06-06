import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.dependencies import get_db_session, get_tenant_id
from app.schemas.webhook import ExecutionLogResponse, ExecutionLogListResponse
from app.services.webhook_service import get_execution, get_executions

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/executions", tags=["Executions"])


# ── Get paginated execution logs ───────────────────────
@router.get(
    "",
    response_model=ExecutionLogListResponse,
    summary="Get all execution logs for a tenant",
)
async def list_executions(
    db: AsyncSession = Depends(get_db_session),
    tenant_id: str = Depends(get_tenant_id),
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    return await get_executions(
        db=db,
        tenant_id=tenant_id,
        agent_id=agent_id,
        status=status,
        page=page,
        page_size=page_size,
    )


# ── Get single execution by execution_id ──────────────
@router.get(
    "/{execution_id}",
    response_model=ExecutionLogResponse,
    summary="Get a single execution log by execution ID",
)
async def get_execution_by_id(
    execution_id: str,
    db: AsyncSession = Depends(get_db_session),
    tenant_id: str = Depends(get_tenant_id),
):
    return await get_execution(
        db=db,
        execution_id=execution_id,
        tenant_id=tenant_id,
    )