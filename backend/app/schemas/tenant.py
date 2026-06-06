from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict
from datetime import datetime


# ── Create tenant ──────────────────────────────────────
class TenantCreate(BaseModel):
    tenant_id: str = Field(..., description="Unique tenant ID — must match X-Tenant-ID header in Bolna")
    name: str = Field(..., description="Human readable tenant name")
    agent_id: str = Field(..., description="Bolna agent ID linked to this tenant")
    api_key: str = Field(..., description="Expected X-API-Key header value Bolna sends")
    forward_url: Optional[str] = Field(None, description="Downstream URL to forward execution data")
    forward_headers: Optional[Dict[str, str]] = Field(None, description="Extra headers for downstream call")


# ── Update tenant ──────────────────────────────────────
class TenantUpdate(BaseModel):
    name: Optional[str] = None
    api_key: Optional[str] = None
    forward_url: Optional[str] = None
    forward_headers: Optional[Dict[str, str]] = None
    is_active: Optional[bool] = None


# ── Tenant response ────────────────────────────────────
class TenantResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    agent_id: str
    api_key: str
    forward_url: Optional[str] = None
    forward_headers: Optional[Dict[str, str]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Tenant list response ───────────────────────────────
class TenantListResponse(BaseModel):
    total: int
    items: list[TenantResponse]