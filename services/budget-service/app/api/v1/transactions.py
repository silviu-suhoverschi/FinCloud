"""
Transactions API endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.get("/")
async def list_transactions(
    db: AsyncSession = Depends(get_db)
):
    """List all transactions"""
    return {
        "transactions": [],
        "message": "Transactions endpoint - implementation pending"
    }


@router.post("/")
async def create_transaction(
    db: AsyncSession = Depends(get_db)
):
    """Create a new transaction"""
    return {
        "message": "Create transaction endpoint - implementation pending"
    }
