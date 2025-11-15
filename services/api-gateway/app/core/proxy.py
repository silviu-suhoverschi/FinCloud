"""
Service proxy for routing requests to backend services.
"""

from typing import Optional
import httpx
from fastapi import Request, Response, HTTPException, status
import structlog

from app.core.config import settings
from app.middleware.circuit_breaker import circuit_breaker_registry

logger = structlog.get_logger()


class ServiceProxy:
    """
    Proxy for routing requests to backend microservices with circuit breaker protection.
    """

    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None
        self.service_urls = {
            "budget": settings.BUDGET_SERVICE_URL,
            "portfolio": settings.PORTFOLIO_SERVICE_URL,
            "notification": settings.NOTIFICATION_SERVICE_URL,
        }

    async def initialize(self):
        """Initialize HTTP client."""
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(settings.REQUEST_TIMEOUT),
            follow_redirects=True,
        )
        logger.info("Service proxy initialized")

    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()

    async def proxy_request(
        self,
        request: Request,
        service_name: str,
        path: str,
    ) -> Response:
        """
        Proxy request to backend service with circuit breaker protection.

        Args:
            request: Original FastAPI request
            service_name: Name of the target service (budget, portfolio, notification)
            path: Path to forward to the service

        Returns:
            Response: Response from backend service

        Raises:
            HTTPException: If service is unavailable or request fails
        """
        if service_name not in self.service_urls:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unknown service: {service_name}",
            )

        service_url = self.service_urls[service_name]
        target_url = f"{service_url}{path}"

        # Get circuit breaker for this service
        circuit_breaker = circuit_breaker_registry.get_breaker(service_name)

        # Execute request with circuit breaker protection
        try:
            response = circuit_breaker.call(
                self._execute_request,
                request=request,
                target_url=target_url,
                service_name=service_name,
            )
            return await response
        except HTTPException:
            # Re-raise HTTP exceptions (including circuit breaker failures)
            raise
        except Exception as e:
            logger.error(
                "Service request failed",
                service=service_name,
                path=path,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service {service_name} is unavailable: {str(e)}",
            )

    async def _execute_request(
        self, request: Request, target_url: str, service_name: str
    ) -> Response:
        """
        Execute the actual HTTP request to backend service.

        Args:
            request: Original request
            target_url: Full URL to backend service
            service_name: Service name for logging

        Returns:
            Response: FastAPI response

        Raises:
            Exception: If request fails
        """
        # Prepare headers (forward relevant headers, add auth token)
        headers = dict(request.headers)

        # Remove host header to avoid conflicts
        headers.pop("host", None)

        # Add request ID if available
        if hasattr(request.state, "request_id"):
            headers["X-Request-ID"] = request.state.request_id

        # Add user context headers if available
        if hasattr(request.state, "user_id") and request.state.user_id:
            headers["X-User-ID"] = str(request.state.user_id)

        if hasattr(request.state, "user_email") and request.state.user_email:
            headers["X-User-Email"] = request.state.user_email

        if hasattr(request.state, "user_role") and request.state.user_role:
            headers["X-User-Role"] = request.state.user_role

        # Read request body
        body = await request.body()

        # Build query string
        query_string = str(request.query_params)
        if query_string:
            target_url = f"{target_url}?{query_string}"

        logger.debug(
            "Proxying request to service",
            service=service_name,
            method=request.method,
            url=target_url,
            user_id=getattr(request.state, "user_id", None),
        )

        try:
            # Execute request
            response = await self.client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
            )

            # Log response
            logger.debug(
                "Received response from service",
                service=service_name,
                status_code=response.status_code,
            )

            # Create FastAPI response
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type"),
            )

        except httpx.TimeoutException:
            logger.error(
                "Service request timeout",
                service=service_name,
                url=target_url,
                timeout=settings.REQUEST_TIMEOUT,
            )
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"Service {service_name} request timeout",
            )

        except httpx.ConnectError as e:
            logger.error(
                "Failed to connect to service",
                service=service_name,
                url=target_url,
                error=str(e),
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Cannot connect to service {service_name}",
            )

        except Exception as e:
            logger.error(
                "Unexpected error proxying request",
                service=service_name,
                url=target_url,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise


# Global service proxy instance
service_proxy = ServiceProxy()
