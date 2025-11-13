"""
Portfolios API endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.get("/")
async def list_portfolios(db: AsyncSession = Depends(get_db)):
    """List all portfolios"""
    return {"portfolios": [], "message": "Portfolios endpoint - implementation pending"}


@router.post("/")
async def create_portfolio(db: AsyncSession = Depends(get_db)):
    """Create a new portfolio"""
    return {"message": "Create portfolio endpoint - implementation pending"}


@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: int, db: AsyncSession = Depends(get_db)):
    """Get portfolio by ID"""
    return {
        "portfolio_id": portfolio_id,
        "message": "Get portfolio endpoint - implementation pending",
    }
