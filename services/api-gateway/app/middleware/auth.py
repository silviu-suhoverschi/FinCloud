"""
Authentication middleware for API Gateway.
Validates JWT tokens and adds user context to requests.
"""

from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_token, verify_token_type


security = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """
    Middleware to validate JWT tokens and inject user context into requests.
    """

    # Public paths that don't require authentication
    PUBLIC_PATHS = [
        "/",
        "/health",
        "/api/v1/status",
        "/api/v1/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/refresh",
        "/api/v1/auth/password-reset/request",
        "/api/v1/auth/password-reset/confirm",
    ]

    @staticmethod
    def is_public_path(path: str) -> bool:
        """Check if the request path is public."""
        # Exact match
        if path in AuthMiddleware.PUBLIC_PATHS:
            return True

        # Path starts with public prefix
        for public_path in AuthMiddleware.PUBLIC_PATHS:
            if path.startswith(public_path):
                return True

        return False

    @staticmethod
    async def get_token_from_request(request: Request) -> Optional[str]:
        """Extract JWT token from request headers."""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        if not auth_header.startswith("Bearer "):
            return None

        return auth_header.replace("Bearer ", "")

    @staticmethod
    async def validate_and_inject_user(request: Request):
        """
        Validate JWT token and inject user information into request state.

        Raises:
            HTTPException: If token is invalid or missing for protected routes
        """
        # Skip authentication for public paths
        if AuthMiddleware.is_public_path(request.url.path):
            request.state.user_id = None
            request.state.user_email = None
            request.state.user_role = None
            return

        # Get token from request
        token = await AuthMiddleware.get_token_from_request(request)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Decode and validate token
        payload = decode_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify token type
        if not verify_token_type(payload, "access"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Access token required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract user information from token
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Inject user context into request state
        try:
            request.state.user_id = int(user_id)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        request.state.user_email = payload.get("email")
        request.state.user_role = payload.get("role", "user")
        request.state.token = token
