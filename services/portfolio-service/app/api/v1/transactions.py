"""
Portfolio Transactions API endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.get("/")
async def list_transactions(
    db: AsyncSession = Depends(get_db)
):
    """List all portfolio transactions"""
    return {
        "transactions": [],
        "message": "Portfolio transactions endpoint - implementation pending"
    }


@router.post("/")
async def create_transaction(
    db: AsyncSession = Depends(get_db)
):
    """Create a new portfolio transaction (buy/sell/dividend)"""
    return {
        "message": "Create transaction endpoint - implementation pending"
    }
