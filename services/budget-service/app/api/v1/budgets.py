"""
Budgets API endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.get("/")
async def list_budgets(
    db: AsyncSession = Depends(get_db)
):
    """List all budgets"""
    return {
        "budgets": [],
        "message": "Budgets endpoint - implementation pending"
    }


@router.post("/")
async def create_budget(
    db: AsyncSession = Depends(get_db)
):
    """Create a new budget"""
    return {
        "message": "Create budget endpoint - implementation pending"
    }
