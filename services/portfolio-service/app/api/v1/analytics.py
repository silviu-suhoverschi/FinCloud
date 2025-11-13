"""
Portfolio Analytics API endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.get("/performance")
async def get_performance(portfolio_id: int, db: AsyncSession = Depends(get_db)):
    """Get portfolio performance metrics (ROI, XIRR, TWR)"""
    return {
        "portfolio_id": portfolio_id,
        "metrics": {},
        "message": "Performance analytics - implementation pending",
    }


@router.get("/allocation")
async def get_allocation(portfolio_id: int, db: AsyncSession = Depends(get_db)):
    """Get asset allocation breakdown"""
    return {
        "portfolio_id": portfolio_id,
        "allocation": {},
        "message": "Asset allocation - implementation pending",
    }
