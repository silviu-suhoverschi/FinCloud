"""
API Gateway - Central API Gateway for FinCloud

Features:
- Request routing to backend services
- JWT authentication middleware
- Rate limiting (Redis-based)
- Circuit breaker pattern
- Request/response logging
- Health check aggregation
- CORS configuration
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.core.config import settings
from app.core.proxy import service_proxy
from app.middleware.auth import AuthMiddleware
from app.middleware.rate_limit import rate_limiter
from app.middleware.logging import LoggingMiddleware
from app.api.v1 import health, routes

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting API Gateway", environment=settings.ENVIRONMENT)

    # Initialize service proxy
    await service_proxy.initialize()
    logger.info("Service proxy initialized")

    # Initialize rate limiter
    await rate_limiter.initialize()
    logger.info("Rate limiter initialized")

    logger.info(
        "API Gateway started successfully",
        port=settings.SERVICE_PORT,
        cors_origins=settings.CORS_ORIGINS,
        rate_limiting=settings.RATE_LIMIT_ENABLED,
    )

    yield

    # Shutdown
    logger.info("Shutting down API Gateway")

    # Cleanup
    await service_proxy.close()
    await rate_limiter.close()

    logger.info("API Gateway shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="FinCloud API Gateway",
    description="""
    Central API Gateway for FinCloud - A self-hosted personal finance and investment management platform.

    ## Features

    * **Authentication**: JWT-based authentication with automatic token validation
    * **Rate Limiting**: Redis-based rate limiting to prevent abuse
    * **Circuit Breaker**: Automatic failover and recovery for backend services
    * **Request Logging**: Comprehensive request/response logging with timing
    * **Service Routing**: Intelligent routing to microservices (budget, portfolio, notifications)

    ## Services

    * **Budget Service**: Account management, transactions, budgets, and reports
    * **Portfolio Service**: Investment tracking, holdings, and performance analytics
    * **Notification Service**: Email, Telegram, and webhook notifications

    ## Rate Limits

    * **Per Minute**: {}/min per user/IP
    * **Per Hour**: {}/hour per user/IP

    Rate limit headers are included in all responses:
    - `X-RateLimit-Limit-Minute`: Requests allowed per minute
    - `X-RateLimit-Remaining-Minute`: Remaining requests this minute
    - `X-RateLimit-Limit-Hour`: Requests allowed per hour
    - `X-RateLimit-Remaining-Hour`: Remaining requests this hour

    ## Authentication

    Most endpoints require a valid JWT access token in the Authorization header:

    ```
    Authorization: Bearer <your-access-token>
    ```

    Public endpoints (no authentication required):
    - `POST /api/v1/auth/register` - Register new user
    - `POST /api/v1/auth/login` - Login and get tokens
    - `POST /api/v1/auth/refresh` - Refresh access token
    - `POST /api/v1/auth/password-reset/request` - Request password reset
    - `POST /api/v1/auth/password-reset/confirm` - Confirm password reset

    ## Circuit Breaker

    The gateway implements circuit breaker pattern for all backend services:
    - **Closed**: Normal operation, all requests pass through
    - **Open**: Service failing, requests fail fast with 503
    - **Half-Open**: Testing recovery, limited requests allowed

    Check circuit breaker status: `GET /api/v1/health/detailed`
    """.format(
        settings.RATE_LIMIT_PER_MINUTE, settings.RATE_LIMIT_PER_HOUR
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - must be added first
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
    expose_headers=["X-Request-ID", "X-Process-Time", "X-RateLimit-*"],
)

# Logging middleware
app.add_middleware(LoggingMiddleware)


# Authentication middleware
@app.middleware("http")
async def authentication_middleware(request: Request, call_next):
    """Validate JWT tokens and inject user context."""
    try:
        # Validate token and inject user info
        await AuthMiddleware.validate_and_inject_user(request)

        # Continue to next middleware/route
        response = await call_next(request)
        return response

    except HTTPException as e:
        # Return authentication error
        return JSONResponse(
            status_code=e.status_code, content={"detail": e.detail}, headers=e.headers
        )


# Rate limiting middleware
@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    """Check rate limits before processing request."""
    try:
        # Check rate limit
        await rate_limiter.check_rate_limit(request)

        # Continue to next middleware/route
        response = await call_next(request)
        return response

    except HTTPException as e:
        # Return rate limit error
        return JSONResponse(
            status_code=e.status_code, content={"detail": e.detail}, headers=e.headers
        )


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper logging."""
    logger.warning(
        "HTTP exception",
        path=request.url.path,
        status_code=exc.status_code,
        detail=exc.detail,
        user_id=getattr(request.state, "user_id", None),
    )
    return JSONResponse(
        status_code=exc.status_code, content={"detail": exc.detail}, headers=exc.headers
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        error=str(exc),
        error_type=type(exc).__name__,
        user_id=getattr(request.state, "user_id", None),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "service": "api-gateway",
        "version": "0.1.0",
        "status": "operational",
        "description": "FinCloud API Gateway - Central entry point for all services",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
        },
        "services": {
            "budget": f"{settings.BUDGET_SERVICE_URL}",
            "portfolio": f"{settings.PORTFOLIO_SERVICE_URL}",
            "notifications": f"{settings.NOTIFICATION_SERVICE_URL}",
        },
    }


# Include routers
# Health router at root level (for Kubernetes/Docker health checks)
app.include_router(health.router, tags=["Health"])

# Also include health router under /api/v1 for consistency
app.include_router(health.router, prefix="/api/v1", tags=["Health API"])

app.include_router(routes.router, prefix="/api/v1", tags=["Services"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        log_level=settings.LOG_LEVEL.lower(),
    )
