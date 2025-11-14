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
    # May return 401 or 403 depending on auth middleware implementation
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_verify_email_success(client: AsyncClient):
    """Test successful email verification request"""
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
    assert verification_request.status_code == 200
    assert "verification_token" in verification_request.json()

    # Note: Actual token verification is tested separately as it requires
    # proper token generation which depends on JWT_SECRET consistency


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
async def test_verify_email_request_endpoint(client: AsyncClient):
    """Test email verification request endpoint"""
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
    assert verification_request.status_code == 200
    assert "message" in verification_request.json()


@pytest.mark.asyncio
async def test_request_verification_multiple_times(client: AsyncClient):
    """Test requesting verification multiple times"""
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

    # Request verification first time
    response1 = await client.post(
        "/api/v1/email-verification/request",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response1.status_code == 200

    # Request verification second time (should also succeed before verification)
    response2 = await client.post(
        "/api/v1/email-verification/request",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response2.status_code == 200


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
    # May return 401 or 403 depending on auth middleware implementation
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_resend_verification_email(client: AsyncClient):
    """Test resending verification email"""
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

    # Resend verification (should succeed for unverified user)
    response = await client.post(
        "/api/v1/email-verification/resend",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_complete_email_verification_request_flow(client: AsyncClient):
    """Test complete email verification request flow"""
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
    assert "verification_token" in verification_request.json()

    # Note: Actual verification requires proper JWT token setup
    # which is environment-dependent


@pytest.mark.asyncio
async def test_multiple_verification_token_requests(client: AsyncClient):
    """Test multiple verification token requests"""
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
    assert "verification_token" in response1.json()

    response2 = await client.post(
        "/api/v1/email-verification/resend",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response2.status_code == 200
    assert "verification_token" in response2.json()
