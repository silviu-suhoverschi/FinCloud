"""
Health check endpoints for API Gateway.
Aggregates health from all backend services.
"""

import httpx
from fastapi import APIRouter
from typing import Dict, Any
import structlog

from app.core.config import settings
from app.middleware.circuit_breaker import circuit_breaker_registry
from app.middleware.rate_limit import rate_limiter

logger = structlog.get_logger()

router = APIRouter()


async def check_service_health(service_name: str, service_url: str) -> Dict[str, Any]:
    """
    Check health of a single service.

    Args:
        service_name: Name of the service
        service_url: Base URL of the service

    Returns:
        dict: Health status information
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{service_url}/health")

            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time_ms": int(response.elapsed.total_seconds() * 1000),
                    "details": response.json() if response.content else {},
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "response_time_ms": int(response.elapsed.total_seconds() * 1000),
                }
    except httpx.TimeoutException:
        return {"status": "unhealthy", "error": "Timeout"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@router.get("/health")
async def health_check():
    """
    Simple health check for the API Gateway itself.
    """
    return {"status": "healthy", "service": "api-gateway", "version": "0.1.0"}


@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check including all backend services.
    """
    # Check backend services
    services = {
        "budget_service": settings.BUDGET_SERVICE_URL,
        "portfolio_service": settings.PORTFOLIO_SERVICE_URL,
        "notification_service": settings.NOTIFICATION_SERVICE_URL,
    }

    service_health = {}
    for service_name, service_url in services.items():
        service_health[service_name] = await check_service_health(
            service_name, service_url
        )

    # Check Redis
    redis_status = "unknown"
    if rate_limiter.redis_client:
        try:
            await rate_limiter.redis_client.ping()
            redis_status = "healthy"
        except Exception as e:
            redis_status = f"unhealthy: {str(e)}"
    else:
        redis_status = "not configured"

    # Determine overall status
    all_services_healthy = all(
        s["status"] == "healthy" for s in service_health.values()
    )

    overall_status = "healthy" if all_services_healthy else "degraded"

    return {
        "status": overall_status,
        "service": "api-gateway",
        "version": "0.1.0",
        "services": service_health,
        "redis": redis_status,
        "circuit_breakers": circuit_breaker_registry.get_all_states(),
    }


@router.get("/health/ready")
async def readiness_check():
    """
    Readiness probe for Kubernetes.
    Returns 200 if gateway is ready to accept traffic.
    """
    # Check if critical dependencies are available
    redis_ready = False
    if rate_limiter.redis_client:
        try:
            await rate_limiter.redis_client.ping()
            redis_ready = True
        except Exception:
            pass

    # Gateway is ready if Redis is available (rate limiter dependency)
    # Backend services can be down temporarily (circuit breaker will handle)
    if redis_ready or not settings.RATE_LIMIT_ENABLED:
        return {"status": "ready"}
    else:
        return {"status": "not ready", "reason": "Redis unavailable"}, 503


@router.get("/health/live")
async def liveness_check():
    """
    Liveness probe for Kubernetes.
    Returns 200 if gateway is alive (not deadlocked).
    """
    return {"status": "alive"}


@router.get("/status")
async def api_status():
    """
    API status endpoint with service information.
    """
    return {
        "api_version": "v1",
        "gateway_version": "0.1.0",
        "services": {
            "budget_service": settings.BUDGET_SERVICE_URL,
            "portfolio_service": settings.PORTFOLIO_SERVICE_URL,
            "notification_service": settings.NOTIFICATION_SERVICE_URL,
        },
        "features": {
            "authentication": True,
            "rate_limiting": settings.RATE_LIMIT_ENABLED,
            "circuit_breaker": True,
            "cors": True,
        },
    }
