"""
Request/response logging middleware for API Gateway.
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all requests and responses with timing information.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response: HTTP response
        """
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Get client information
        client_ip = request.client.host if request.client else "unknown"
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()

        # Start timing
        start_time = time.time()

        # Log incoming request
        logger.info(
            "Incoming request",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
            client_ip=client_ip,
            user_agent=request.headers.get("User-Agent", "unknown"),
            user_id=getattr(request.state, "user_id", None),
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}"

            # Add rate limit headers if available
            if hasattr(request.state, "rate_limit_headers"):
                for key, value in request.state.rate_limit_headers.items():
                    response.headers[key] = value

            # Log response
            logger.info(
                "Request completed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                process_time=f"{process_time:.4f}s",
                user_id=getattr(request.state, "user_id", None),
            )

            return response

        except Exception as e:
            # Calculate processing time even on error
            process_time = time.time() - start_time

            # Log error
            logger.error(
                "Request failed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                error=str(e),
                error_type=type(e).__name__,
                process_time=f"{process_time:.4f}s",
                user_id=getattr(request.state, "user_id", None),
            )

            # Re-raise exception to be handled by FastAPI
            raise
