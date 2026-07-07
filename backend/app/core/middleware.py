"""Middleware for checking site access password header against configuration."""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import get_settings

class PasswordGateMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Bypass CORS preflight requests (OPTIONS)
        if request.method == "OPTIONS":
            return await call_next(request)

        # 2. Bypass OpenAPI developer docs routes
        path = request.url.path.rstrip("/")
        if path.startswith("/docs") or path.startswith("/redoc") or path == "/openapi.json":
            return await call_next(request)

        settings = get_settings()
        required_password = settings.site_access_password

        # 3. If password is set, verify the custom header
        if required_password:
            provided_password = request.headers.get("X-Site-Access-Password")
            if provided_password != required_password:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Unauthorized: Site access password required or invalid."}
                )

        return await call_next(request)
