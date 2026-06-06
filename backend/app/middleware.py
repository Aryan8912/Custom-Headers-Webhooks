import os
import time
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class IPWhitelistMiddleware:

    def __init__(self, app, whitelist_ip: str):
        self.app = app
        self.whitelist_ip = whitelist_ip

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            path = request.url.path

            if path.startswith("/webhook/bolna"):
                client_ip = self._get_client_ip(request)
                app_env = os.getenv("APP_ENV", "development")

                if app_env == "production" and client_ip != self.whitelist_ip:
                    logger.warning(f"Blocked request from unauthorized IP: {client_ip}")
                    response = JSONResponse(
                        status_code=403,
                        content={"error": "Forbidden", "detail": f"IP '{client_ip}' is not allowed"},
                    )
                    await response(scope, receive, send)
                    return

        await self.app(scope, receive, send)

    def _get_client_ip(self, request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


class RequestLoggingMiddleware:

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        start_time = time.time()
        status_code = 500

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        await self.app(scope, receive, send_wrapper)

        duration = (time.time() - start_time) * 1000
        logger.info(
            f"{request.method} {request.url.path} "
            f"status={status_code} "
            f"duration={duration:.2f}ms "
            f"tenant={request.headers.get('X-Tenant-ID', '-')}"
        )


def register_middlewares(app: FastAPI):
    from app.config import get_settings
    settings = get_settings()
    app.add_middleware(IPWhitelistMiddleware, whitelist_ip=settings.BOLNA_SENDER_IP)
    app.add_middleware(RequestLoggingMiddleware)