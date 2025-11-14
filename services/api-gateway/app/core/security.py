"""
Security utilities for JWT token validation in API Gateway.
No database access - tokens are validated cryptographically only.
"""

from typing import Any, Optional
from jose import JWTError, jwt
from app.core.config import settings


def decode_token(token: str) -> Optional[dict[str, Any]]:
    """
    Decode and validate a JWT token.

    Args:
        token: The JWT token to decode

    Returns:
        dict: The decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_token_type(payload: dict[str, Any], expected_type: str) -> bool:
    """
    Verify the token type matches the expected type.

    Args:
        payload: The decoded token payload
        expected_type: The expected token type ("access" or "refresh")

    Returns:
        bool: True if token type matches, False otherwise
    """
    token_type = payload.get("type")
    return token_type == expected_type


def get_user_id_from_token(token: str) -> Optional[int]:
    """
    Extract user ID from JWT token.

    Args:
        token: The JWT token

    Returns:
        int: User ID if valid, None otherwise
    """
    payload = decode_token(token)
    if payload is None:
        return None

    if not verify_token_type(payload, "access"):
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    try:
        return int(user_id)
    except (ValueError, TypeError):
        return None


def get_user_email_from_token(token: str) -> Optional[str]:
    """
    Extract user email from JWT token.

    Args:
        token: The JWT token

    Returns:
        str: User email if present in token, None otherwise
    """
    payload = decode_token(token)
    if payload is None:
        return None

    return payload.get("email")


def get_user_role_from_token(token: str) -> Optional[str]:
    """
    Extract user role from JWT token.

    Args:
        token: The JWT token

    Returns:
        str: User role if present in token, None otherwise
    """
    payload = decode_token(token)
    if payload is None:
        return None

    return payload.get("role")
