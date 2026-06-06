from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


# ── Custom exceptions ──────────────────────────────────

class WebhookAuthError(Exception):
    """Raised when Authorization or X-API-Key header is invalid."""
    def __init__(self, message: str = "Unauthorized"):
        self.message = message
        super().__init__(message)


class TenantNotFoundError(Exception):
    """Raised when X-Tenant-ID header does not match any tenant."""
    def __init__(self, tenant_id: str):
        self.message = f"Tenant '{tenant_id}' not found or inactive"
        super().__init__(self.message)


class InvalidIPError(Exception):
    """Raised when request comes from an IP not in the whitelist."""
    def __init__(self, ip: str):
        self.message = f"Requests from IP '{ip}' are not allowed"
        super().__init__(self.message)


class ExecutionNotFoundError(Exception):
    """Raised when an execution_id does not exist in the DB."""
    def __init__(self, execution_id: str):
        self.message = f"Execution '{execution_id}' not found"
        super().__init__(self.message)


class ForwardingError(Exception):
    """Raised when downstream forwarding fails after all retries."""
    def __init__(self, url: str, status_code: int):
        self.message = f"Forwarding to '{url}' failed with status {status_code}"
        super().__init__(self.message)


# ── Register all handlers on the FastAPI app ──────────

def register_exception_handlers(app: FastAPI):

    @app.exception_handler(WebhookAuthError)
    async def webhook_auth_handler(request: Request, exc: WebhookAuthError):
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized", "detail": exc.message},
        )

    @app.exception_handler(TenantNotFoundError)
    async def tenant_not_found_handler(request: Request, exc: TenantNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"error": "Tenant Not Found", "detail": exc.message},
        )

    @app.exception_handler(InvalidIPError)
    async def invalid_ip_handler(request: Request, exc: InvalidIPError):
        return JSONResponse(
            status_code=403,
            content={"error": "Forbidden", "detail": exc.message},
        )

    @app.exception_handler(ExecutionNotFoundError)
    async def execution_not_found_handler(request: Request, exc: ExecutionNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"error": "Not Found", "detail": exc.message},
        )

    @app.exception_handler(ForwardingError)
    async def forwarding_error_handler(request: Request, exc: ForwardingError):
        return JSONResponse(
            status_code=502,
            content={"error": "Bad Gateway", "detail": exc.message},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "detail": str(exc)},
        )