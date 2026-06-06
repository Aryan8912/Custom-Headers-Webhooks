from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):

    # ── App ────────────────────────────────────────────
    APP_ENV: str = "development"

    # ── Database ───────────────────────────────────────
    DATABASE_URL: str

    # ── Redis ──────────────────────────────────────────
    REDIS_URL: str

    # ── Bolna ──────────────────────────────────────────
    BOLNA_API_KEY: str
    BOLNA_WEBHOOK_SECRET: str
    BOLNA_SENDER_IP: str = "13.203.39.153"

    # ── Auth headers Bolna sends to your endpoint ──────
    SECRET_KEY: str
    X_API_KEY: str

    # ── Multi-tenant ───────────────────────────────────
    ALLOWED_TENANT_IDS: str = "tenant_a"

    # ── Derived: parse ALLOWED_TENANT_IDS into a list ──
    @property
    def tenant_list(self) -> List[str]:
        return [t.strip() for t in self.ALLOWED_TENANT_IDS.split(",")]

    # ── Derived: is this a test run ────────────────────
    @property
    def is_testing(self) -> bool:
        return self.APP_ENV == "testing"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


def get_settings() -> Settings:
    return Settings()