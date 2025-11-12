"""
Authentication service for user registration, login, and token management.
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, Token, AccessToken
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type,
)


class AuthService:
    """Service class for authentication operations."""

    @staticmethod
    async def register_user(user_data: UserRegister, db: AsyncSession) -> User:
        """
        Register a new user.

        Args:
            user_data: User registration data
            db: Database session

        Returns:
            User: The created user

        Raises:
            HTTPException: If email already exists
        """
        # Check if email already exists
        result = await db.execute(select(User).filter(User.email == user_data.email.lower()))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Hash the password
        password_hash = get_password_hash(user_data.password)

        # Create new user
        new_user = User(
            email=user_data.email.lower(),
            password_hash=password_hash,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            preferred_currency=user_data.preferred_currency,
            timezone=user_data.timezone,
            role="user",  # Default role
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user

    @staticmethod
    async def authenticate_user(login_data: UserLogin, db: AsyncSession) -> User:
        """
        Authenticate a user with email and password.

        Args:
            login_data: User login credentials
            db: Database session

        Returns:
            User: The authenticated user

        Raises:
            HTTPException: If credentials are invalid
        """
        # Find user by email
        result = await db.execute(select(User).filter(User.email == login_data.email.lower()))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user account",
            )

        # Update last login timestamp
        user.last_login_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    def create_tokens(user: User) -> Token:
        """
        Create access and refresh tokens for a user.

        Args:
            user: The user to create tokens for

        Returns:
            Token: Access and refresh tokens
        """
        # Create token data
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }

        # Create tokens
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    @staticmethod
    async def refresh_access_token(refresh_token: str, db: AsyncSession) -> AccessToken:
        """
        Refresh an access token using a refresh token.

        Args:
            refresh_token: The refresh token
            db: Database session

        Returns:
            AccessToken: New access token

        Raises:
            HTTPException: If refresh token is invalid
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        # Decode the refresh token
        payload = decode_token(refresh_token)
        if payload is None:
            raise credentials_exception

        # Verify token type
        if not verify_token_type(payload, "refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user_id from payload
        user_id: Optional[int] = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Query user from database
        result = await db.execute(select(User).filter(User.id == int(user_id)))
        user = result.scalar_one_or_none()

        if user is None:
            raise credentials_exception

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user account",
            )

        # Create new access token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }
        access_token = create_access_token(token_data)

        return AccessToken(access_token=access_token, token_type="bearer")

    @staticmethod
    async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
        """
        Get a user by email address.

        Args:
            email: User's email address
            db: Database session

        Returns:
            User: The user if found, None otherwise
        """
        result = await db.execute(select(User).filter(User.email == email.lower()))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_user_password(user: User, new_password: str, db: AsyncSession) -> User:
        """
        Update a user's password.

        Args:
            user: The user to update
            new_password: The new password (plain text)
            db: Database session

        Returns:
            User: The updated user
        """
        user.password_hash = get_password_hash(new_password)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def verify_user_email(user: User, db: AsyncSession) -> User:
        """
        Mark a user's email as verified.

        Args:
            user: The user to verify
            db: Database session

        Returns:
            User: The verified user
        """
        user.is_verified = True
        user.email_verified_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
        return user
