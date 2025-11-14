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
async def test_reset_password_success(client: AsyncClient):
    """Test successful password reset"""
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
    reset_token = reset_request.json()["reset_token"]

    # Reset password
    response = await client.post(
        "/api/v1/password-reset/reset",
        json={
            "token": reset_token,
            "new_password": "NewPassword123",
        },
    )
    assert response.status_code == 200
    assert "successfully" in response.json()["message"].lower()

    # Verify can login with new password
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "resetpass@example.com",
            "password": "NewPassword123",
        },
    )
    assert login_response.status_code == 200

    # Verify cannot login with old password
    old_login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "resetpass@example.com",
            "password": "OldPassword123",
        },
    )
    assert old_login_response.status_code == 401


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
async def test_complete_password_reset_flow(client: AsyncClient):
    """Test complete password reset flow"""
    email = "completeflow@example.com"
    old_password = "OldPassword123"
    new_password = "NewPassword456"

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
    reset_token = reset_request.json()["reset_token"]

    # 4. Reset password
    reset_response = await client.post(
        "/api/v1/password-reset/reset",
        json={
            "token": reset_token,
            "new_password": new_password,
        },
    )
    assert reset_response.status_code == 200

    # 5. Verify cannot login with old password
    login_old_fail = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": old_password,
        },
    )
    assert login_old_fail.status_code == 401

    # 6. Verify can login with new password
    login_new = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": new_password,
        },
    )
    assert login_new.status_code == 200
    assert "access_token" in login_new.json()


@pytest.mark.asyncio
async def test_multiple_password_reset_requests(client: AsyncClient):
    """Test multiple password reset requests"""
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
    token1 = response1.json()["reset_token"]

    response2 = await client.post(
        "/api/v1/password-reset/request",
        json={"email": "multiple@example.com"},
    )
    assert response2.status_code == 200
    token2 = response2.json()["reset_token"]

    # Both tokens should be valid (in this implementation)
    # Use the second token
    reset_response = await client.post(
        "/api/v1/password-reset/reset",
        json={
            "token": token2,
            "new_password": "NewPassword123",
        },
    )
    assert reset_response.status_code == 200

    # Verify new password works
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "multiple@example.com",
            "password": "NewPassword123",
        },
    )
    assert login_response.status_code == 200
