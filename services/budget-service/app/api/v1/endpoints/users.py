"""
User profile management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user, RoleChecker
from app.core.security import verify_password, get_password_hash
from app.schemas.auth import UserResponse, UserUpdate, PasswordChange
from app.models.user import User

router = APIRouter()


@router.get(
    "/profile",
    response_model=UserResponse,
    summary="Get user profile",
    description="Get the current user's profile information",
)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user's profile.

    Requires authentication (Bearer token in Authorization header).
    Returns the user's complete profile information.
    """
    return UserResponse.model_validate(current_user)


@router.patch(
    "/profile",
    response_model=UserResponse,
    summary="Update user profile",
    description="Update the current user's profile information",
)
async def update_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user profile information.

    Requires authentication (Bearer token in Authorization header).

    - **first_name**: User's first name
    - **last_name**: User's last name
    - **preferred_currency**: Preferred currency code (3 letters)
    - **timezone**: User's timezone

    Returns the updated user profile.
    """
    # Update fields if provided
    if profile_data.first_name is not None:
        current_user.first_name = profile_data.first_name

    if profile_data.last_name is not None:
        current_user.last_name = profile_data.last_name

    if profile_data.preferred_currency is not None:
        current_user.preferred_currency = profile_data.preferred_currency

    if profile_data.timezone is not None:
        current_user.timezone = profile_data.timezone

    # Update timestamp
    current_user.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(current_user)

    return UserResponse.model_validate(current_user)


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change password",
    description="Change the current user's password",
)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change user password.

    Requires authentication (Bearer token in Authorization header).

    - **current_password**: Current password for verification
    - **new_password**: New password (min 8 chars, must contain uppercase, lowercase, digit)

    Returns 204 No Content on success.
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )

    # Check that new password is different from current
    if password_data.current_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password",
        )

    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()

    await db.commit()

    return None


@router.delete(
    "/account",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user account",
    description="Soft delete the current user's account",
)
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete user account (soft delete).

    Requires authentication (Bearer token in Authorization header).

    This performs a soft delete by:
    - Setting is_active to False
    - Setting deleted_at timestamp
    - Keeping data for audit purposes

    Returns 204 No Content on success.
    """
    # Soft delete
    current_user.is_active = False
    current_user.deleted_at = datetime.utcnow()
    current_user.updated_at = datetime.utcnow()

    await db.commit()

    return None


# Admin endpoints


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID (Admin only)",
    description="Get any user's information by ID. Requires admin role.",
    dependencies=[Depends(RoleChecker(["admin"]))],
)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get user information by ID.

    **Admin only endpoint.**

    - **user_id**: The ID of the user to retrieve

    Returns the user's profile information.
    """
    from sqlalchemy import select

    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(user)


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
    summary="Update user role (Admin only)",
    description="Update a user's role. Requires admin role.",
    dependencies=[Depends(RoleChecker(["admin"]))],
)
async def update_user_role(
    user_id: int,
    role: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Update user role.

    **Admin only endpoint.**

    - **user_id**: The ID of the user to update
    - **role**: New role (user, admin, premium)

    Returns the updated user profile.
    """
    from sqlalchemy import select

    # Validate role
    valid_roles = ["user", "admin", "premium"]
    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}",
        )

    # Get user
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update role
    user.role = role
    user.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.patch(
    "/{user_id}/activate",
    response_model=UserResponse,
    summary="Activate user account (Admin only)",
    description="Reactivate a deactivated user account. Requires admin role.",
    dependencies=[Depends(RoleChecker(["admin"]))],
)
async def activate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Activate user account.

    **Admin only endpoint.**

    - **user_id**: The ID of the user to activate

    Returns the updated user profile.
    """
    from sqlalchemy import select

    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Activate user
    user.is_active = True
    user.deleted_at = None
    user.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)
