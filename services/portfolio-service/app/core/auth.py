"""
Authentication dependencies for FastAPI Portfolio Service.

Note: This service doesn't manage users directly. User authentication is handled
by the Budget Service. We only validate JWT tokens and extract user_id.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import decode_token, verify_token_type

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    """
    Dependency to get the current authenticated user ID from JWT token.

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        int: The authenticated user's ID

    Raises:
        HTTPException: If token is invalid or user_id not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode the token
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    # Verify token type
    if not verify_token_type(payload, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user_id from payload
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    return int(user_id)
