"""
Categories API endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.get("/")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """List all categories"""
    return {"categories": [], "message": "Categories endpoint - implementation pending"}


@router.post("/")
async def create_category(db: AsyncSession = Depends(get_db)):
    """Create a new category"""
    return {"message": "Create category endpoint - implementation pending"}
