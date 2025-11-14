"""
Route handlers for proxying requests to backend services.
"""

from fastapi import APIRouter, Request, Response
import structlog

from app.core.proxy import service_proxy

logger = structlog.get_logger()

router = APIRouter()


# Budget Service Routes
@router.api_route(
    "/budget/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    include_in_schema=False,
)
async def proxy_to_budget_service(request: Request, path: str) -> Response:
    """
    Proxy all requests to budget service.

    This catches all routes under /api/v1/budget/* and forwards them
    to the budget service.
    """
    # Forward to budget service with the original path
    service_path = f"/api/v1/{path}"
    return await service_proxy.proxy_request(
        request=request, service_name="budget", path=service_path
    )


# Portfolio Service Routes
@router.api_route(
    "/portfolio/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    include_in_schema=False,
)
async def proxy_to_portfolio_service(request: Request, path: str) -> Response:
    """
    Proxy all requests to portfolio service.

    This catches all routes under /api/v1/portfolio/* and forwards them
    to the portfolio service.
    """
    # Forward to portfolio service with the original path
    service_path = f"/api/v1/{path}"
    return await service_proxy.proxy_request(
        request=request, service_name="portfolio", path=service_path
    )


# Notification Service Routes
@router.api_route(
    "/notifications/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    include_in_schema=False,
)
async def proxy_to_notification_service(request: Request, path: str) -> Response:
    """
    Proxy all requests to notification service.

    This catches all routes under /api/v1/notifications/* and forwards them
    to the notification service.
    """
    # Forward to notification service with the original path
    service_path = f"/api/v1/{path}"
    return await service_proxy.proxy_request(
        request=request, service_name="notification", path=service_path
    )


# Auth routes - forward to budget service (where User model lives)
@router.api_route(
    "/auth/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    include_in_schema=False,
)
async def proxy_auth_routes(request: Request, path: str) -> Response:
    """
    Proxy authentication routes to budget service.

    Auth endpoints are handled by budget service since that's where
    the User model and authentication logic resides.
    """
    service_path = f"/api/v1/auth/{path}"
    return await service_proxy.proxy_request(
        request=request, service_name="budget", path=service_path
    )


# Users routes - forward to budget service
@router.api_route(
    "/users/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    include_in_schema=False,
)
async def proxy_users_routes(request: Request, path: str) -> Response:
    """
    Proxy user management routes to budget service.
    """
    service_path = f"/api/v1/users/{path}"
    return await service_proxy.proxy_request(
        request=request, service_name="budget", path=service_path
    )
