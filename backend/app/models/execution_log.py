import uuid
from sqlalchemy import String, Text, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin


class ExecutionLog(Base, TimestampMixin):
    __tablename__ = "execution_logs"

    # ── Primary key ────────────────────────────────────
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # ── Bolna identifiers ──────────────────────────────
    execution_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,       # query by execution_id frequently
    )

    agent_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,       # query by agent_id frequently
    )

    # ── Tenant routing ─────────────────────────────────
    tenant_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    # ── Call status from Bolna ─────────────────────────
    # scheduled | queued | in_progress | completed | failed
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # ── Full raw payload from Bolna ────────────────────
    payload: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    # ── HTTP verification ──────────────────────────────
    auth_verified: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    # ── Downstream forwarding ──────────────────────────
    forwarded: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    forward_status_code: Mapped[int] = mapped_column(
        Integer,
        nullable=True,    # null until forwarded
    )

    forward_error: Mapped[str] = mapped_column(
        Text,
        nullable=True,    # null if no error
    )

    def __repr__(self) -> str:
        return (
            f"<ExecutionLog id={self.id} "
            f"execution_id={self.execution_id} "
            f"status={self.status} "
            f"tenant={self.tenant_id}>"
        )