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


# Accounts routes - forward to budget service
@router.api_route(
    "/accounts/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    include_in_schema=False,
)
async def proxy_accounts_routes(request: Request, path: str) -> Response:
    """
    Proxy account management routes to budget service.
    """
    service_path = f"/api/v1/accounts/{path}"
    return await service_proxy.proxy_request(
        request=request, service_name="budget", path=service_path
    )


# Accounts root route - forward to budget service
@router.api_route(
    "/accounts",
    methods=["GET", "POST"],
    include_in_schema=False,
)
async def proxy_accounts_root(request: Request) -> Response:
    """
    Proxy account root routes to budget service.
    """
    service_path = "/api/v1/accounts"
    return await service_proxy.proxy_request(
        request=request, service_name="budget", path=service_path
    )


# Transactions routes - forward to budget service
@router.api_route(
    "/transactions/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    include_in_schema=False,
)
async def proxy_transactions_routes(request: Request, path: str) -> Response:
    """
    Proxy transaction management routes to budget service.
    """
    service_path = f"/api/v1/transactions/{path}"
    return await service_proxy.proxy_request(
        request=request, service_name="budget", path=service_path
    )


# Transactions root route - forward to budget service
@router.api_route(
    "/transactions",
    methods=["GET", "POST"],
    include_in_schema=False,
)
async def proxy_transactions_root(request: Request) -> Response:
    """
    Proxy transaction root routes to budget service.
    """
    service_path = "/api/v1/transactions"
    return await service_proxy.proxy_request(
        request=request, service_name="budget", path=service_path
    )


# Budgets routes - forward to budget service
@router.api_route(
    "/budgets/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    include_in_schema=False,
)
async def proxy_budgets_routes(request: Request, path: str) -> Response:
    """
    Proxy budget management routes to budget service.
    """
    service_path = f"/api/v1/budgets/{path}"
    return await service_proxy.proxy_request(
        request=request, service_name="budget", path=service_path
    )


# Budgets root route - forward to budget service
@router.api_route(
    "/budgets",
    methods=["GET", "POST"],
    include_in_schema=False,
)
async def proxy_budgets_root(request: Request) -> Response:
    """
    Proxy budget root routes to budget service.
    """
    service_path = "/api/v1/budgets"
    return await service_proxy.proxy_request(
        request=request, service_name="budget", path=service_path
    )


# Categories routes - forward to budget service
@router.api_route(
    "/categories/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    include_in_schema=False,
)
async def proxy_categories_routes(request: Request, path: str) -> Response:
    """
    Proxy category management routes to budget service.
    """
    service_path = f"/api/v1/categories/{path}"
    return await service_proxy.proxy_request(
        request=request, service_name="budget", path=service_path
    )


# Categories root route - forward to budget service
@router.api_route(
    "/categories",
    methods=["GET", "POST"],
    include_in_schema=False,
)
async def proxy_categories_root(request: Request) -> Response:
    """
    Proxy category root routes to budget service.
    """
    service_path = "/api/v1/categories"
    return await service_proxy.proxy_request(
        request=request, service_name="budget", path=service_path
    )


# Reports routes - forward to budget service
@router.api_route(
    "/reports/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    include_in_schema=False,
)
async def proxy_reports_routes(request: Request, path: str) -> Response:
    """
    Proxy report routes to budget service.
    """
    service_path = f"/api/v1/reports/{path}"
    return await service_proxy.proxy_request(
        request=request, service_name="budget", path=service_path
    )


# Reports root route - forward to budget service
@router.api_route(
    "/reports",
    methods=["GET", "POST"],
    include_in_schema=False,
)
async def proxy_reports_root(request: Request) -> Response:
    """
    Proxy report root routes to budget service.
    """
    service_path = "/api/v1/reports"
    return await service_proxy.proxy_request(
        request=request, service_name="budget", path=service_path
    )


# Portfolios routes - forward to portfolio service
@router.api_route(
    "/portfolios/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    include_in_schema=False,
)
async def proxy_portfolios_routes(request: Request, path: str) -> Response:
    """
    Proxy portfolio management routes to portfolio service.
    """
    service_path = f"/api/v1/portfolios/{path}"
    return await service_proxy.proxy_request(
        request=request, service_name="portfolio", path=service_path
    )


# Portfolios root route - forward to portfolio service
@router.api_route(
    "/portfolios",
    methods=["GET", "POST"],
    include_in_schema=False,
)
async def proxy_portfolios_root(request: Request) -> Response:
    """
    Proxy portfolio root routes to portfolio service.
    """
    service_path = "/api/v1/portfolios"
    return await service_proxy.proxy_request(
        request=request, service_name="portfolio", path=service_path
    )


# Holdings routes - forward to portfolio service
@router.api_route(
    "/holdings/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    include_in_schema=False,
)
async def proxy_holdings_routes(request: Request, path: str) -> Response:
    """
    Proxy holdings management routes to portfolio service.
    """
    service_path = f"/api/v1/holdings/{path}"
    return await service_proxy.proxy_request(
        request=request, service_name="portfolio", path=service_path
    )


# Holdings root route - forward to portfolio service
@router.api_route(
    "/holdings",
    methods=["GET", "POST"],
    include_in_schema=False,
)
async def proxy_holdings_root(request: Request) -> Response:
    """
    Proxy holdings root routes to portfolio service.
    """
    service_path = "/api/v1/holdings"
    return await service_proxy.proxy_request(
        request=request, service_name="portfolio", path=service_path
    )


# Analytics routes - forward to portfolio service
@router.api_route(
    "/analytics/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    include_in_schema=False,
)
async def proxy_analytics_routes(request: Request, path: str) -> Response:
    """
    Proxy analytics routes to portfolio service.
    """
    service_path = f"/api/v1/analytics/{path}"
    return await service_proxy.proxy_request(
        request=request, service_name="portfolio", path=service_path
    )


# Analytics root route - forward to portfolio service
@router.api_route(
    "/analytics",
    methods=["GET", "POST"],
    include_in_schema=False,
)
async def proxy_analytics_root(request: Request) -> Response:
    """
    Proxy analytics root routes to portfolio service.
    """
    service_path = "/api/v1/analytics"
    return await service_proxy.proxy_request(
        request=request, service_name="portfolio", path=service_path
    )


# Assets routes - forward to portfolio service
@router.api_route(
    "/assets/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    include_in_schema=False,
)
async def proxy_assets_routes(request: Request, path: str) -> Response:
    """
    Proxy assets routes to portfolio service.
    """
    service_path = f"/api/v1/assets/{path}"
    return await service_proxy.proxy_request(
        request=request, service_name="portfolio", path=service_path
    )


# Assets root route - forward to portfolio service
@router.api_route(
    "/assets",
    methods=["GET", "POST"],
    include_in_schema=False,
)
async def proxy_assets_root(request: Request) -> Response:
    """
    Proxy assets root routes to portfolio service.
    """
    service_path = "/api/v1/assets"
    return await service_proxy.proxy_request(
        request=request, service_name="portfolio", path=service_path
    )
