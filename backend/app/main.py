import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from app.config import get_settings
from app.db import init_db
from app.cache import close_redis
from app.middleware import register_middlewares
from app.exceptions import register_exception_handlers
from app.routes import webhook, executions, health

# import models so Base knows about them before init_db()
from app.models import execution_log, tenant

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()


# ── Lifespan: startup + shutdown ───────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):

    # ── Startup ────────────────────────────────────────
    logger.info(f"Starting Bolna Webhook Receiver [{settings.APP_ENV}]")
    await init_db()
    logger.info("✅ Database tables ready")
    yield

    # ── Shutdown ───────────────────────────────────────
    await close_redis()
    logger.info("✅ Redis connection closed")
    logger.info("Bolna Webhook Receiver stopped")


# ── App factory ────────────────────────────────────────
def create_app() -> FastAPI:

    app = FastAPI(
        title="Bolna Webhook Receiver",
        description=(
            "Receives execution-data webhooks from Bolna Analytics tab. "
            "Verifies custom headers (Authorization, X-API-Key, X-Tenant-ID), "
            "stores execution logs, and forwards to downstream services."
        ),
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS ───────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Skip ngrok browser warning ─────────────────────
    @app.middleware("http")
    async def add_ngrok_header(request: Request, call_next):
        response = await call_next(request)
        response.headers["ngrok-skip-browser-warning"] = "true"
        return response

    # ── Custom middlewares ─────────────────────────────
    register_middlewares(app)

    # ── Exception handlers ─────────────────────────────
    register_exception_handlers(app)

    # ── Routers ────────────────────────────────────────
    app.include_router(health.router)
    app.include_router(webhook.router)
    app.include_router(executions.router)

    return app


# ── App instance ───────────────────────────────────────
app = create_app()