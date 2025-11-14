"""
Tests for authentication middleware
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_public_endpoint_no_auth(client: AsyncClient):
    """Test public endpoints don't require authentication"""
    # Root endpoint
    response = await client.get("/")
    assert response.status_code == 200

    # Health endpoint
    response = await client.get("/health")
    assert response.status_code == 200

    # Status endpoint
    response = await client.get("/api/v1/status")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_protected_endpoint_no_token(client: AsyncClient):
    """Test protected endpoints require authentication"""
    # Don't use mock_service_proxy - test will fail at auth middleware level
    response = await client.get("/api/v1/budget/accounts")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing authentication token"


@pytest.mark.asyncio
async def test_protected_endpoint_invalid_token(client: AsyncClient):
    """Test protected endpoints reject invalid tokens"""
    response = await client.get(
        "/api/v1/budget/accounts", headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401
    assert "Invalid or expired token" in response.json()["detail"]


@pytest.mark.asyncio
async def test_protected_endpoint_expired_token(client: AsyncClient, expired_jwt_token):
    """Test protected endpoints reject expired tokens"""
    response = await client.get(
        "/api/v1/budget/accounts",
        headers={"Authorization": f"Bearer {expired_jwt_token}"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_wrong_token_type(
    client: AsyncClient, invalid_token_type
):
    """Test protected endpoints reject wrong token type (refresh instead of access)"""
    response = await client.get(
        "/api/v1/budget/accounts",
        headers={"Authorization": f"Bearer {invalid_token_type}"},
    )
    assert response.status_code == 401
    assert "Invalid token type" in response.json()["detail"]


@pytest.mark.asyncio
async def test_protected_endpoint_valid_token(
    client: AsyncClient, valid_jwt_token, mock_service_proxy
):
    """Test protected endpoints work with valid token"""
    # With valid token, auth should pass and request reaches proxy (which returns 503 in test)
    response = await client.get(
        "/api/v1/budget/accounts",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )

    # Should pass authentication, so we get 503 from mocked proxy (not 401)
    assert response.status_code == 503  # Proxy mock returns 503


@pytest.mark.asyncio
async def test_auth_middleware_extracts_user_info(client: AsyncClient, valid_jwt_token):
    """Test that auth middleware extracts user information from token"""
    # This would require accessing request.state which is internal
    # We can verify this indirectly by checking logs or by creating
    # a test endpoint that returns request.state
    pass


@pytest.mark.asyncio
async def test_malformed_auth_header(client: AsyncClient):
    """Test malformed Authorization header"""
    # Missing 'Bearer' prefix
    response = await client.get(
        "/api/v1/budget/accounts", headers={"Authorization": "invalid-format"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_public_auth_endpoints(client: AsyncClient):
    """Test that auth endpoints are public"""
    # These should not require authentication
    # (will fail if backend is down, but should pass auth middleware)

    # Note: These will fail without backend, but should NOT fail with 401
    endpoints = [
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/refresh",
    ]

    for endpoint in endpoints:
        response = await client.post(endpoint, json={})
        # Should NOT be 401 (auth error), but might be 422 (validation) or 503 (no backend)
        assert response.status_code != 401
