import os

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

_UNPROTECTED = {"/health"}


class ApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in _UNPROTECTED:
            return await call_next(request)

        expected = os.environ.get("API_KEY")
        if not expected:
            # API_KEY not configured — open access (dev / initial setup)
            return await call_next(request)

        provided = request.headers.get("X-API-Key")
        if not provided or provided != expected:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        return await call_next(request)
