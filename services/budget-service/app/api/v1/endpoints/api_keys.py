"""
API Keys management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import secrets
import hashlib

from app.core.database import get_db
from app.core.auth import get_current_user
from app.schemas.api_key import (
    ApiKeyCreate,
    ApiKeyResponse,
    ApiKeyWithSecret,
    ApiKeyUpdate,
)
from app.models.user import User
from app.models.api_key import ApiKey

router = APIRouter()


def generate_api_key() -> tuple[str, str, str]:
    """
    Generate a new API key.

    Returns:
        tuple: (key, key_hash, key_prefix)
    """
    # Generate a random API key (32 bytes = 64 hex chars)
    key = f"fck_{secrets.token_urlsafe(32)}"  # fck = FinCloud Key

    # Hash the key for storage
    key_hash = hashlib.sha256(key.encode()).hexdigest()

    # Store first 12 chars as prefix for display (e.g., "fck_ABC...")
    key_prefix = key[:12]

    return key, key_hash, key_prefix


@router.get(
    "",
    response_model=list[ApiKeyResponse],
    summary="List API keys",
    description="Get all API keys for the current user",
)
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all API keys for the current user.

    Returns a list of API keys (without the actual secret keys).
    """
    result = await db.execute(
        select(ApiKey)
        .filter(ApiKey.user_id == current_user.id)
        .order_by(ApiKey.created_at.desc())
    )
    api_keys = result.scalars().all()

    return [ApiKeyResponse.model_validate(key) for key in api_keys]


@router.post(
    "",
    response_model=ApiKeyWithSecret,
    status_code=status.HTTP_201_CREATED,
    summary="Create API key",
    description="Create a new API key. The secret key is returned only once!",
)
async def create_api_key(
    api_key_data: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new API key.

    **IMPORTANT**: The secret key is returned only once. Save it securely!

    Returns the created API key with the actual secret.
    """
    # Generate API key
    key, key_hash, key_prefix = generate_api_key()

    # Create API key record
    api_key = ApiKey(
        user_id=current_user.id,
        name=api_key_data.name,
        description=api_key_data.description,
        key_hash=key_hash,
        key_prefix=key_prefix,
        permissions=api_key_data.permissions,
        expires_at=api_key_data.expires_at,
    )

    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    # Return response with the actual key (only shown once!)
    response = ApiKeyWithSecret.model_validate(api_key)
    response.key = key

    return response


@router.get(
    "/{key_id}",
    response_model=ApiKeyResponse,
    summary="Get API key",
    description="Get details of a specific API key",
)
async def get_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get API key details.

    Returns the API key information (without the actual secret).
    """
    result = await db.execute(
        select(ApiKey).filter(
            ApiKey.id == key_id,
            ApiKey.user_id == current_user.id,
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    return ApiKeyResponse.model_validate(api_key)


@router.patch(
    "/{key_id}",
    response_model=ApiKeyResponse,
    summary="Update API key",
    description="Update an API key's details",
)
async def update_api_key(
    key_id: int,
    api_key_data: ApiKeyUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update API key details.

    Can update name, description, permissions, and active status.
    Cannot update the actual key itself.
    """
    result = await db.execute(
        select(ApiKey).filter(
            ApiKey.id == key_id,
            ApiKey.user_id == current_user.id,
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    # Update fields if provided
    if api_key_data.name is not None:
        api_key.name = api_key_data.name

    if api_key_data.description is not None:
        api_key.description = api_key_data.description

    if api_key_data.permissions is not None:
        api_key.permissions = api_key_data.permissions

    if api_key_data.is_active is not None:
        api_key.is_active = api_key_data.is_active

    api_key.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(api_key)

    return ApiKeyResponse.model_validate(api_key)


@router.delete(
    "/{key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete API key",
    description="Delete an API key permanently",
)
async def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an API key permanently.

    This action cannot be undone.
    """
    result = await db.execute(
        select(ApiKey).filter(
            ApiKey.id == key_id,
            ApiKey.user_id == current_user.id,
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    await db.delete(api_key)
    await db.commit()

    return None
