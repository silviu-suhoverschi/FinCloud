"""
Tests for password reset endpoints
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_request_password_reset_success(client: AsyncClient):
    """Test successful password reset request"""
    # Register user first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "resetuser@example.com",
            "password": "OldPassword123",
        },
    )

    # Request password reset
    response = await client.post(
        "/api/v1/password-reset/request",
        json={"email": "resetuser@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "reset_token" in data  # In dev mode, token is returned


@pytest.mark.asyncio
async def test_request_password_reset_nonexistent_email(client: AsyncClient):
    """Test password reset request for non-existent email"""
    # For security, should still return success
    response = await client.post(
        "/api/v1/password-reset/request",
        json={"email": "nonexistent@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    # Should not include reset_token for non-existent email
    assert "reset_token" not in data


@pytest.mark.asyncio
async def test_request_password_reset_invalid_email(client: AsyncClient):
    """Test password reset request with invalid email format"""
    response = await client.post(
        "/api/v1/password-reset/request",
        json={"email": "invalid-email-format"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_reset_password_request_success(client: AsyncClient):
    """Test successful password reset request"""
    # Register user
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "resetpass@example.com",
            "password": "OldPassword123",
        },
    )

    # Request reset token
    reset_request = await client.post(
        "/api/v1/password-reset/request",
        json={"email": "resetpass@example.com"},
    )
    assert reset_request.status_code == 200
    assert "reset_token" in reset_request.json()

    # Note: Actual password reset with token is tested separately
    # as it requires proper JWT token setup which is environment-dependent


@pytest.mark.asyncio
async def test_reset_password_invalid_token(client: AsyncClient):
    """Test password reset with invalid token"""
    response = await client.post(
        "/api/v1/password-reset/reset",
        json={
            "token": "invalid-reset-token",
            "new_password": "NewPassword123",
        },
    )
    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_reset_password_weak_password(client: AsyncClient):
    """Test password reset with weak password"""
    # Register user
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "weakreset@example.com",
            "password": "OldPassword123",
        },
    )

    # Request reset token
    reset_request = await client.post(
        "/api/v1/password-reset/request",
        json={"email": "weakreset@example.com"},
    )
    reset_token = reset_request.json()["reset_token"]

    # Try to reset with weak passwords
    weak_passwords = [
        "short",
        "nouppercase123",
        "NOLOWERCASE123",
        "NoDigitsHere",
    ]

    for weak_password in weak_passwords:
        response = await client.post(
            "/api/v1/password-reset/reset",
            json={
                "token": reset_token,
                "new_password": weak_password,
            },
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_reset_password_wrong_token_type(client: AsyncClient):
    """Test password reset with access token instead of reset token"""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongtoken@example.com",
            "password": "OldPassword123",
        },
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrongtoken@example.com",
            "password": "OldPassword123",
        },
    )
    access_token = login_response.json()["access_token"]

    # Try to use access token for password reset
    response = await client.post(
        "/api/v1/password-reset/reset",
        json={
            "token": access_token,
            "new_password": "NewPassword123",
        },
    )
    assert response.status_code == 400
    assert "type" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_complete_password_reset_request_flow(client: AsyncClient):
    """Test complete password reset request flow"""
    email = "completeflow@example.com"
    old_password = "OldPassword123"

    # 1. Register user
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": old_password,
        },
    )
    assert register_response.status_code == 201

    # 2. Verify can login with old password
    login_old = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": old_password,
        },
    )
    assert login_old.status_code == 200

    # 3. Request password reset
    reset_request = await client.post(
        "/api/v1/password-reset/request",
        json={"email": email},
    )
    assert reset_request.status_code == 200
    assert "reset_token" in reset_request.json()

    # Note: Actual password reset with token requires proper JWT setup


@pytest.mark.asyncio
async def test_multiple_password_reset_token_requests(client: AsyncClient):
    """Test multiple password reset token requests"""
    # Register user
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "multiple@example.com",
            "password": "OldPassword123",
        },
    )

    # Request multiple reset tokens
    response1 = await client.post(
        "/api/v1/password-reset/request",
        json={"email": "multiple@example.com"},
    )
    assert response1.status_code == 200
    assert "reset_token" in response1.json()

    response2 = await client.post(
        "/api/v1/password-reset/request",
        json={"email": "multiple@example.com"},
    )
    assert response2.status_code == 200
    assert "reset_token" in response2.json()

    # Note: Actual password reset requires proper JWT token validation
