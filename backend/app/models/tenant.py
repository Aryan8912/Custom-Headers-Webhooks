import uuid
from sqlalchemy import String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"

    # ── Primary key ────────────────────────────────────
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # ── Tenant identity ────────────────────────────────
    tenant_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,        # X-Tenant-ID header value
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # ── Bolna agent linked to this tenant ──────────────
    agent_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    # ── Auth header values set in Bolna Analytics tab ──
    # These are what Bolna sends on every webhook POST
    api_key: Mapped[str] = mapped_column(
        String(512),
        nullable=False,    # X-API-Key header value
    )

    # ── Downstream forwarding config ───────────────────
    forward_url: Mapped[str] = mapped_column(
        String(512),
        nullable=True,     # optional: forward to CRM etc.
    )

    forward_headers: Mapped[dict] = mapped_column(
        JSON,
        nullable=True,     # extra headers for downstream
    )

    # ── Status ─────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Tenant id={self.id} "
            f"tenant_id={self.tenant_id} "
            f"agent_id={self.agent_id} "
            f"active={self.is_active}>"
        )