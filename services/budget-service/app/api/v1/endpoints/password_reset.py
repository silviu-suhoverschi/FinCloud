"""
Password reset endpoints.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, decode_token
from app.schemas.auth import PasswordResetRequest, PasswordReset
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/request",
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Request a password reset token for a user account",
)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Request a password reset.

    - **email**: User's email address

    Returns a success message. In production, this would send an email with a reset link.
    For security, we always return success even if the email doesn't exist.

    **Note**: This is a simplified implementation. In production, you should:
    1. Generate a unique reset token
    2. Store it in the database or Redis with an expiration
    3. Send an email with a reset link containing the token
    4. Implement rate limiting to prevent abuse
    """
    # Get user by email
    user = await AuthService.get_user_by_email(reset_request.email, db)

    if user:
        # Generate a password reset token (valid for 1 hour)
        reset_token_data = {
            "sub": str(user.id),
            "email": user.email,
            "type": "password_reset",
        }
        reset_token = create_access_token(
            reset_token_data, expires_delta=timedelta(hours=1)
        )

        # TODO: Send email with reset token
        # For now, we'll just return the token in development
        # In production, this should be sent via email and NOT returned in response
        return {
            "message": "If an account exists with this email, a password reset link has been sent.",
            "reset_token": reset_token,  # REMOVE THIS IN PRODUCTION
            "note": "In production, this token should be sent via email, not returned in the API response.",
        }

    # Always return success for security (don't reveal if email exists)
    return {
        "message": "If an account exists with this email, a password reset link has been sent."
    }


@router.post(
    "/reset",
    status_code=status.HTTP_200_OK,
    summary="Reset password",
    description="Reset password using a reset token",
)
async def reset_password(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_db),
):
    """
    Reset password using a reset token.

    - **token**: Password reset token (received via email)
    - **new_password**: New password (min 8 chars, must contain uppercase, lowercase, digit)

    Returns a success message.
    """
    # Decode the reset token
    payload = decode_token(reset_data.token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Verify token type
    token_type = payload.get("type")
    if token_type != "password_reset":
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
    from app.models.user import User

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

    # Update password
    await AuthService.update_user_password(user, reset_data.new_password, db)

    return {
        "message": "Password has been reset successfully. You can now login with your new password."
    }
