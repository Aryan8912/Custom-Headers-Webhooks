from pydantic import BaseModel, Field, model_validator
from typing import Optional, Any
from datetime import datetime


# ── Bolna incoming payload ─────────────────────────────
# Bolna sends "id" not "execution_id"
class BolnaWebhookPayload(BaseModel):

    # Bolna's actual field name is "id"
    id: Optional[str] = Field(None, description="Bolna execution ID")
    execution_id: Optional[str] = Field(None, description="Execution ID alias")

    agent_id: str = Field(..., description="Bolna agent ID")
    status: str = Field(..., description="Call status from Bolna")

    # call data
    transcript: Optional[str] = Field(None)
    recording_url: Optional[str] = Field(None)
    conversation_duration: Optional[float] = Field(None)
    total_cost: Optional[float] = Field(None)
    error_message: Optional[str] = Field(None)
    summary: Optional[str] = Field(None)

    # numbers
    user_number: Optional[str] = Field(None)
    agent_number: Optional[str] = Field(None)

    # timestamps
    initiated_at: Optional[str] = Field(None)
    created_at: Optional[str] = Field(None)
    updated_at: Optional[str] = Field(None)

    # derive execution_id from id if not provided
    @model_validator(mode="after")
    def set_execution_id(self):
        if not self.execution_id and self.id:
            self.execution_id = self.id
        return self

    model_config = {"extra": "allow"}


# ── Webhook received response ──────────────────────────
class WebhookAckResponse(BaseModel):
    status: str = "queued"
    execution_id: str
    message: str = "Webhook received and queued for processing"


# ── Execution log response ─────────────────────────────
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