"""
Holdings API endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.get("/")
async def list_holdings(
    db: AsyncSession = Depends(get_db)
):
    """List all holdings"""
    return {
        "holdings": [],
        "message": "Holdings endpoint - implementation pending"
    }
