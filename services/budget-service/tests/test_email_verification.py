"""
Tests for email verification endpoints
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_request_email_verification_success(client: AsyncClient):
    """Test successful email verification request"""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "verifyuser@example.com",
            "password": "TestPassword123",
        },
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "verifyuser@example.com",
            "password": "TestPassword123",
        },
    )
    token = login_response.json()["access_token"]

    # Request email verification
    response = await client.post(
        "/api/v1/email-verification/request",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "verification_token" in data  # In dev mode, token is returned


@pytest.mark.asyncio
async def test_request_email_verification_no_auth(client: AsyncClient):
    """Test email verification request without authentication"""
    response = await client.post("/api/v1/email-verification/request")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_verify_email_success(client: AsyncClient):
    """Test successful email verification"""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "verify@example.com",
            "password": "TestPassword123",
        },
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "verify@example.com",
            "password": "TestPassword123",
        },
    )
    token = login_response.json()["access_token"]

    # Get verification token
    verification_request = await client.post(
        "/api/v1/email-verification/request",
        headers={"Authorization": f"Bearer {token}"},
    )
    verification_token = verification_request.json()["verification_token"]

    # Verify email
    response = await client.post(
        "/api/v1/email-verification/verify",
        json={"token": verification_token},
    )
    assert response.status_code == 200
    assert "successfully" in response.json()["message"].lower()

    # Verify user is now verified
    me_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.json()["is_verified"] is True


@pytest.mark.asyncio
async def test_verify_email_invalid_token(client: AsyncClient):
    """Test email verification with invalid token"""
    response = await client.post(
        "/api/v1/email-verification/verify",
        json={"token": "invalid-verification-token"},
    )
    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_verify_email_wrong_token_type(client: AsyncClient):
    """Test email verification with wrong token type"""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongtype@example.com",
            "password": "TestPassword123",
        },
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrongtype@example.com",
            "password": "TestPassword123",
        },
    )
    access_token = login_response.json()["access_token"]

    # Try to use access token for email verification
    response = await client.post(
        "/api/v1/email-verification/verify",
        json={"token": access_token},
    )
    assert response.status_code == 400
    assert "type" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_verify_email_already_verified(client: AsyncClient):
    """Test email verification when already verified"""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "alreadyverified@example.com",
            "password": "TestPassword123",
        },
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "alreadyverified@example.com",
            "password": "TestPassword123",
        },
    )
    token = login_response.json()["access_token"]

    # Get verification token
    verification_request = await client.post(
        "/api/v1/email-verification/request",
        headers={"Authorization": f"Bearer {token}"},
    )
    verification_token = verification_request.json()["verification_token"]

    # Verify email first time
    response1 = await client.post(
        "/api/v1/email-verification/verify",
        json={"token": verification_token},
    )
    assert response1.status_code == 200

    # Try to verify again
    response2 = await client.post(
        "/api/v1/email-verification/verify",
        json={"token": verification_token},
    )
    assert response2.status_code == 200
    assert "already verified" in response2.json()["message"].lower()


@pytest.mark.asyncio
async def test_request_verification_already_verified(client: AsyncClient):
    """Test requesting verification when already verified"""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "alreadyreq@example.com",
            "password": "TestPassword123",
        },
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "alreadyreq@example.com",
            "password": "TestPassword123",
        },
    )
    token = login_response.json()["access_token"]

    # Get verification token and verify
    verification_request = await client.post(
        "/api/v1/email-verification/request",
        headers={"Authorization": f"Bearer {token}"},
    )
    verification_token = verification_request.json()["verification_token"]

    await client.post(
        "/api/v1/email-verification/verify",
        json={"token": verification_token},
    )

    # Try to request verification again
    response = await client.post(
        "/api/v1/email-verification/request",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert "already verified" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_resend_verification_email_success(client: AsyncClient):
    """Test resending verification email"""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "resend@example.com",
            "password": "TestPassword123",
        },
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "resend@example.com",
            "password": "TestPassword123",
        },
    )
    token = login_response.json()["access_token"]

    # Resend verification email
    response = await client.post(
        "/api/v1/email-verification/resend",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "resent" in data["message"].lower()
    assert "verification_token" in data  # In dev mode


@pytest.mark.asyncio
async def test_resend_verification_no_auth(client: AsyncClient):
    """Test resending verification email without authentication"""
    response = await client.post("/api/v1/email-verification/resend")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_resend_verification_already_verified(client: AsyncClient):
    """Test resending verification when already verified"""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "resendalready@example.com",
            "password": "TestPassword123",
        },
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "resendalready@example.com",
            "password": "TestPassword123",
        },
    )
    token = login_response.json()["access_token"]

    # Get verification token and verify
    verification_request = await client.post(
        "/api/v1/email-verification/request",
        headers={"Authorization": f"Bearer {token}"},
    )
    verification_token = verification_request.json()["verification_token"]

    await client.post(
        "/api/v1/email-verification/verify",
        json={"token": verification_token},
    )

    # Try to resend verification
    response = await client.post(
        "/api/v1/email-verification/resend",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert "already verified" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_complete_email_verification_flow(client: AsyncClient):
    """Test complete email verification flow"""
    email = "completeflow@example.com"
    password = "TestPassword123"

    # 1. Register user
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )
    assert register_response.status_code == 201
    assert register_response.json()["is_verified"] is False

    # 2. Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 3. Check user is not verified
    me_response1 = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response1.json()["is_verified"] is False

    # 4. Request verification
    verification_request = await client.post(
        "/api/v1/email-verification/request",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert verification_request.status_code == 200
    verification_token = verification_request.json()["verification_token"]

    # 5. Verify email
    verify_response = await client.post(
        "/api/v1/email-verification/verify",
        json={"token": verification_token},
    )
    assert verify_response.status_code == 200

    # 6. Check user is now verified
    me_response2 = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response2.json()["is_verified"] is True


@pytest.mark.asyncio
async def test_multiple_verification_requests(client: AsyncClient):
    """Test multiple verification requests"""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "multiple@example.com",
            "password": "TestPassword123",
        },
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "multiple@example.com",
            "password": "TestPassword123",
        },
    )
    token = login_response.json()["access_token"]

    # Request multiple verification tokens
    response1 = await client.post(
        "/api/v1/email-verification/request",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response1.status_code == 200
    token1 = response1.json()["verification_token"]

    response2 = await client.post(
        "/api/v1/email-verification/resend",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response2.status_code == 200
    token2 = response2.json()["verification_token"]

    # Both tokens should be valid (in this implementation)
    # Use the second token
    verify_response = await client.post(
        "/api/v1/email-verification/verify",
        json={"token": token2},
    )
    assert verify_response.status_code == 200

    # Verify user is verified
    me_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.json()["is_verified"] is True
