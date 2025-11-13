"""
Email verification endpoints.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.security import create_access_token, decode_token
from app.schemas.auth import EmailVerificationRequest
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter()


@router.post(
    "/request",
    status_code=status.HTTP_200_OK,
    summary="Request email verification",
    description="Request an email verification token to verify user account",
)
async def request_email_verification(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Request email verification.

    Requires authentication (Bearer token in Authorization header).

    Returns a success message. In production, this would send an email with a verification link.

    **Note**: This is a simplified implementation. In production, you should:
    1. Generate a unique verification token
    2. Store it in the database or Redis with an expiration
    3. Send an email with a verification link containing the token
    4. Implement rate limiting to prevent abuse
    """
    # Check if user is already verified
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified",
        )

    # Generate a verification token (valid for 24 hours)
    verification_token_data = {
        "sub": str(current_user.id),
        "email": current_user.email,
        "type": "email_verification",
    }
    verification_token = create_access_token(
        verification_token_data, expires_delta=timedelta(hours=24)
    )

    # TODO: Send email with verification token
    # For now, we'll just return the token in development
    # In production, this should be sent via email and NOT returned in response
    return {
        "message": "Verification email has been sent to your email address.",
        "verification_token": verification_token,  # REMOVE THIS IN PRODUCTION
        "note": (
            "In production, this token should be sent via email, "
            "not returned in the API response."
        ),
    }


@router.post(
    "/verify",
    status_code=status.HTTP_200_OK,
    summary="Verify email",
    description="Verify email address using a verification token",
)
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify email address using a verification token.

    - **token**: Email verification token (received via email)

    Returns a success message.
    """
    # Decode the verification token
    payload = decode_token(verification_data.token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    # Verify token type
    token_type = payload.get("type")
    if token_type != "email_verification":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type",
        )

    # Get user_id from payload
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token payload",
        )

    # Get user from database
    from sqlalchemy import select

    result = await db.execute(select(User).filter(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active",
        )

    # Check if already verified
    if user.is_verified:
        return {
            "message": "Email is already verified.",
        }

    # Verify email
    await AuthService.verify_user_email(user, db)

    return {
        "message": (
            "Email has been verified successfully. "
            "You now have full access to your account."
        )
    }


@router.post(
    "/resend",
    status_code=status.HTTP_200_OK,
    summary="Resend verification email",
    description="Resend email verification token",
)
async def resend_verification_email(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Resend verification email.

    Requires authentication (Bearer token in Authorization header).

    Returns a success message.

    **Note**: This endpoint has the same implementation as /request for MVP.
    In production, you may want to add rate limiting to prevent abuse.
    """
    # Check if user is already verified
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified",
        )

    # Generate a verification token (valid for 24 hours)
    verification_token_data = {
        "sub": str(current_user.id),
        "email": current_user.email,
        "type": "email_verification",
    }
    verification_token = create_access_token(
        verification_token_data, expires_delta=timedelta(hours=24)
    )

    # TODO: Send email with verification token
    # For now, we'll just return the token in development
    # In production, this should be sent via email and NOT returned in response
    return {
        "message": "Verification email has been resent to your email address.",
        "verification_token": verification_token,  # REMOVE THIS IN PRODUCTION
        "note": (
            "In production, this token should be sent via email, "
            "not returned in the API response."
        ),
    }
