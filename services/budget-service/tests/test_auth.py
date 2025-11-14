"""
Tests for authentication endpoints
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Test successful user registration"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "TestPassword123",
            "first_name": "Test",
            "last_name": "User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["first_name"] == "Test"
    assert data["last_name"] == "User"
    assert "password" not in data
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test registration with duplicate email"""
    user_data = {
        "email": "duplicate@example.com",
        "password": "TestPassword123",
    }

    # First registration
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201

    # Second registration with same email
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    """Test registration with invalid email"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "invalid-email",
            "password": "TestPassword123",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    """Test registration with weak password"""
    weak_passwords = [
        "short",  # Too short
        "nouppercase123",  # No uppercase
        "NOLOWERCASE123",  # No lowercase
        "NoDigitsHere",  # No digits
    ]

    for password in weak_passwords:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"test{password}@example.com",
                "password": password,
            },
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful login"""
    # Register user first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "loginuser@example.com",
            "password": "TestPassword123",
        },
    )

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "TestPassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Test login with wrong password"""
    # Register user first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongpass@example.com",
            "password": "TestPassword123",
        },
    )

    # Login with wrong password
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "WrongPassword123",
        },
    )
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent user"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "TestPassword123",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_success(client: AsyncClient):
    """Test getting current user info"""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "getme@example.com",
            "password": "TestPassword123",
            "first_name": "Get Me",
            "last_name": "User",
        },
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "getme@example.com",
            "password": "TestPassword123",
        },
    )
    token = login_response.json()["access_token"]

    # Get current user
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "getme@example.com"
    assert data["first_name"] == "Get Me"
    assert data["last_name"] == "User"
    assert "password" not in data


@pytest.mark.asyncio
async def test_get_me_no_token(client: AsyncClient):
    """Test getting current user without token"""
    response = await client.get("/api/v1/auth/me")
    # May return 401 or 403 depending on auth middleware implementation
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_get_me_invalid_token(client: AsyncClient):
    """Test getting current user with invalid token"""
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_success(client: AsyncClient):
    """Test refreshing access token"""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "refresh@example.com",
            "password": "TestPassword123",
        },
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "refresh@example.com",
            "password": "TestPassword123",
        },
    )
    refresh_token = login_response.json()["refresh_token"]

    # Refresh token
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_token_invalid(client: AsyncClient):
    """Test refreshing with invalid token"""
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid-refresh-token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_wrong_type(client: AsyncClient):
    """Test refreshing with access token instead of refresh token"""
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

    # Try to use access token as refresh token
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": access_token},
    )
    assert response.status_code == 401
    assert "type" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_logout_success(client: AsyncClient):
    """Test logout"""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "logout@example.com",
            "password": "TestPassword123",
        },
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "logout@example.com",
            "password": "TestPassword123",
        },
    )
    token = login_response.json()["access_token"]

    # Logout
    response = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_logout_no_token(client: AsyncClient):
    """Test logout without token"""
    response = await client.post("/api/v1/auth/logout")
    # May return 401 or 403 depending on auth middleware implementation
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_full_authentication_flow(client: AsyncClient):
    """Test complete authentication flow"""
    # 1. Register
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "fullflow@example.com",
            "password": "TestPassword123",
            "first_name": "Full Flow",
            "last_name": "User",
        },
    )
    assert register_response.status_code == 201

    # 2. Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "fullflow@example.com",
            "password": "TestPassword123",
        },
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # 3. Access protected endpoint
    me_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "fullflow@example.com"

    # 4. Refresh token
    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 200
    new_access_token = refresh_response.json()["access_token"]

    # 5. Use new access token
    me_response2 = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {new_access_token}"},
    )
    assert me_response2.status_code == 200

    # 6. Logout
    logout_response = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {new_access_token}"},
    )
    assert logout_response.status_code == 204
