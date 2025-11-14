"""
Tests for security utilities
"""

import pytest
from datetime import datetime, timezone, timedelta
from jose import jwt
from app.core.config import settings
from app.core.security import (
    decode_token,
    verify_token_type,
    get_user_id_from_token,
    get_user_email_from_token,
    get_user_role_from_token
)


def create_token(payload_override=None, secret=None):
    """Helper to create test tokens"""
    payload = {
        "sub": "123",
        "email": "test@example.com",
        "role": "user",
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }

    if payload_override:
        payload.update(payload_override)

    return jwt.encode(
        payload,
        secret or settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )


def test_decode_valid_token():
    """Test decoding a valid token"""
    token = create_token()
    payload = decode_token(token)

    assert payload is not None
    assert payload["sub"] == "123"
    assert payload["email"] == "test@example.com"
    assert payload["role"] == "user"
    assert payload["type"] == "access"


def test_decode_invalid_token():
    """Test decoding an invalid token"""
    payload = decode_token("invalid-token")
    assert payload is None


def test_decode_expired_token():
    """Test decoding an expired token"""
    token = create_token({
        "exp": datetime.now(timezone.utc) - timedelta(minutes=10)
    })

    payload = decode_token(token)
    assert payload is None


def test_decode_token_wrong_secret():
    """Test decoding token with wrong secret"""
    token = create_token(secret="wrong-secret")
    payload = decode_token(token)
    assert payload is None


def test_verify_token_type_access():
    """Test verifying access token type"""
    payload = {"type": "access"}
    assert verify_token_type(payload, "access") is True
    assert verify_token_type(payload, "refresh") is False


def test_verify_token_type_refresh():
    """Test verifying refresh token type"""
    payload = {"type": "refresh"}
    assert verify_token_type(payload, "refresh") is True
    assert verify_token_type(payload, "access") is False


def test_verify_token_type_missing():
    """Test verifying token type when type is missing"""
    payload = {}
    assert verify_token_type(payload, "access") is False


def test_get_user_id_from_token():
    """Test extracting user ID from token"""
    token = create_token({"sub": "456"})
    user_id = get_user_id_from_token(token)
    assert user_id == 456


def test_get_user_id_from_invalid_token():
    """Test extracting user ID from invalid token"""
    user_id = get_user_id_from_token("invalid-token")
    assert user_id is None


def test_get_user_id_from_wrong_token_type():
    """Test extracting user ID from wrong token type"""
    token = create_token({"type": "refresh"})
    user_id = get_user_id_from_token(token)
    assert user_id is None


def test_get_user_id_missing_sub():
    """Test extracting user ID when sub is missing"""
    token = create_token({"sub": None})
    user_id = get_user_id_from_token(token)
    assert user_id is None


def test_get_user_id_invalid_format():
    """Test extracting user ID when sub is not a number"""
    token = create_token({"sub": "not-a-number"})
    user_id = get_user_id_from_token(token)
    assert user_id is None


def test_get_user_email_from_token():
    """Test extracting email from token"""
    token = create_token({"email": "user@example.com"})
    email = get_user_email_from_token(token)
    assert email == "user@example.com"


def test_get_user_email_from_invalid_token():
    """Test extracting email from invalid token"""
    email = get_user_email_from_token("invalid-token")
    assert email is None


def test_get_user_email_missing():
    """Test extracting email when email is missing"""
    token = create_token({"email": None})
    email = get_user_email_from_token(token)
    assert email is None


def test_get_user_role_from_token():
    """Test extracting role from token"""
    token = create_token({"role": "admin"})
    role = get_user_role_from_token(token)
    assert role == "admin"


def test_get_user_role_from_invalid_token():
    """Test extracting role from invalid token"""
    role = get_user_role_from_token("invalid-token")
    assert role is None


def test_get_user_role_missing():
    """Test extracting role when role is missing"""
    token = create_token({"role": None})
    role = get_user_role_from_token(token)
    assert role is None


def test_token_with_all_fields():
    """Test token with all user information"""
    token = create_token({
        "sub": "789",
        "email": "admin@example.com",
        "role": "admin",
        "type": "access"
    })

    user_id = get_user_id_from_token(token)
    email = get_user_email_from_token(token)
    role = get_user_role_from_token(token)

    assert user_id == 789
    assert email == "admin@example.com"
    assert role == "admin"
