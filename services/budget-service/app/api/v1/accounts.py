"""
Accounts API endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.get("/")
async def list_accounts(
    db: AsyncSession = Depends(get_db)
):
    """List all accounts"""
    return {
        "accounts": [],
        "message": "Accounts endpoint - implementation pending"
    }


@router.post("/")
async def create_account(
    db: AsyncSession = Depends(get_db)
):
    """Create a new account"""
    return {
        "message": "Create account endpoint - implementation pending"
    }


@router.get("/{account_id}")
async def get_account(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get account by ID"""
    return {
        "account_id": account_id,
        "message": "Get account endpoint - implementation pending"
    }
