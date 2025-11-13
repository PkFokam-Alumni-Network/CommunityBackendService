import time
import uuid
from typing import Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from core.logging_config import ACCESS_LOGGER, LOGGER


class LoggingMiddleware(BaseHTTPMiddleware):
    EXCLUDED_PATHS = ["/health"]

    def _get_request_body_summary(self, request: Request) -> Optional[str]:
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type or "application/x-www-form-urlencoded" in content_type:
            return f"Content-Type: {content_type}"
        return None

    def _get_user_context(self, request: Request) -> dict:
        user_context = {}
        if hasattr(request.state, "user") and request.state.user:
            user = request.state.user
            user_context["user_id"] = getattr(user, "id", None)
            user_context["user_email"] = getattr(user, "email", None)
        return user_context

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.time()

        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        LOGGER.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "endpoint": request.url.path,
                "query_params": str(request.query_params) if request.query_params else None,
                "client_host": client_ip,
                "user_agent": user_agent,
            }
        )

        try:
            response = await call_next(request)
            duration_ms = round((time.time() - start_time) * 1000, 2)

            ACCESS_LOGGER.info(
                f"{request.method} {request.url.path} - {response.status_code} - {duration_ms}ms",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "endpoint": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                }
            )

            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            user_context = self._get_user_context(request)

            error_context = {
                "request_id": request_id,
                "method": request.method,
                "endpoint": request.url.path,
                "query_params": dict(request.query_params) if request.query_params else None,
                "path_params": request.path_params if request.path_params else None,
                "client_host": client_ip,
                "user_agent": user_agent,
                "duration_ms": duration_ms,
                "exception_type": type(e).__name__,
                "exception_message": str(e),
                **user_context,
            }

            body_summary = self._get_request_body_summary(request)
            if body_summary:
                error_context["request_body_info"] = body_summary

            LOGGER.error(
                f"Request failed: {request.method} {request.url.path} - "
                f"{type(e).__name__}: {str(e)}",
                extra=error_context,
                exc_info=True
            )

            raise
