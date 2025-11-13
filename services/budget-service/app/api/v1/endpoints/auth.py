"""
Authentication endpoints for user registration, login, and token management.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    Token,
    TokenRefresh,
    AccessToken,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password",
)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account.

    - **email**: Valid email address (will be validated)
    - **password**: Strong password (min 8 chars, must contain uppercase, lowercase, digit)
    - **first_name**: Optional first name
    - **last_name**: Optional last name
    - **preferred_currency**: Currency code (default: USD)
    - **timezone**: Timezone string (default: UTC)

    Returns the created user information (without password).
    """
    user = await AuthService.register_user(user_data, db)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=Token,
    summary="Login to get access token",
    description="Authenticate with email and password to receive access and refresh tokens",
)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate and receive access tokens.

    - **email**: User's email address
    - **password**: User's password

    Returns both access and refresh tokens.
    The access token should be used for API requests (expires in 30 minutes).
    The refresh token can be used to get a new access token (expires in 7 days).
    """
    user = await AuthService.authenticate_user(login_data, db)
    tokens = AuthService.create_tokens(user)
    return tokens


@router.post(
    "/refresh",
    response_model=AccessToken,
    summary="Refresh access token",
    description="Get a new access token using a refresh token",
)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh an expired access token.

    - **refresh_token**: The refresh token received during login

    Returns a new access token.
    """
    access_token = await AuthService.refresh_access_token(token_data.refresh_token, db)
    return access_token


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the currently authenticated user's information",
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user information.

    Requires authentication (Bearer token in Authorization header).
    Returns the authenticated user's profile information.
    """
    return UserResponse.model_validate(current_user)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout user",
    description="Logout the current user (client-side token removal)",
)
async def logout(
    current_user: User = Depends(get_current_user),
):
    """
    Logout the current user.

    Note: Since we're using JWT tokens, the actual logout is handled client-side
    by removing the tokens. This endpoint confirms authentication and can be used
    to trigger any server-side cleanup if needed in the future.
    """
    # In a JWT-based system, logout is primarily client-side (delete tokens)
    # This endpoint can be used to invalidate tokens in Redis/database if needed
    return None
