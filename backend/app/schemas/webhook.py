from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


# ── Bolna incoming payload ─────────────────────────────
# Shape Bolna POSTs to your Analytics tab webhook URL
class BolnaWebhookPayload(BaseModel):

    execution_id: str = Field(..., description="Bolna execution ID")
    agent_id: str = Field(..., description="Bolna agent ID")

    # scheduled | queued | in_progress | completed | failed
    status: str = Field(..., description="Call status from Bolna")

    # optional fields Bolna may include
    transcript: Optional[str] = Field(None, description="Call transcript")
    recording_url: Optional[str] = Field(None, description="Recording URL")
    duration: Optional[float] = Field(None, description="Call duration in seconds")
    from_number: Optional[str] = Field(None, description="Caller number")
    to_number: Optional[str] = Field(None, description="Recipient number")
    started_at: Optional[datetime] = Field(None, description="Call start time")
    ended_at: Optional[datetime] = Field(None, description="Call end time")

    # catch any extra fields Bolna sends
    model_config = {"extra": "allow"}


# ── Webhook received response ──────────────────────────
# What your endpoint returns to Bolna immediately
class WebhookAckResponse(BaseModel):
    status: str = "queued"
    execution_id: str
    message: str = "Webhook received and queued for processing"


# ── Execution log response ─────────────────────────────
# What GET /executions returns
class ExecutionLogResponse(BaseModel):
    id: str
    execution_id: str
    agent_id: str
    tenant_id: str
    status: str
    auth_verified: bool
    forwarded: bool
    forward_status_code: Optional[int] = None
    forward_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Paginated execution logs ───────────────────────────
class ExecutionLogListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ExecutionLogResponse]