"""
Portfolio Analytics API endpoints
"""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    ComprehensiveAnalytics,
    PerformanceMetrics,
    AssetAllocation,
    HoldingPerformance,
    DividendMetrics,
    PortfolioValueResponse,
    ROIMetrics,
)

router = APIRouter()


@router.get("/portfolio/{portfolio_id}/value", response_model=PortfolioValueResponse)
async def get_portfolio_value(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get total portfolio value

    Calculate the total value of all holdings in the portfolio based on current prices.
    """
    analytics_service = AnalyticsService(db)

    try:
        total_value = await analytics_service.get_portfolio_total_value(portfolio_id)

        # Get portfolio currency
        from app.models.portfolio import Portfolio
        from sqlalchemy import select, and_

        result = await db.execute(
            select(Portfolio).where(
                and_(Portfolio.id == portfolio_id, Portfolio.deleted_at.is_(None))
            )
        )
        portfolio = result.scalar_one_or_none()

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        # Verify ownership
        if portfolio.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this portfolio"
            )

        return PortfolioValueResponse(
            portfolio_id=portfolio_id,
            total_value=total_value,
            currency=portfolio.currency,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate value: {str(e)}")


@router.get("/portfolio/{portfolio_id}/roi", response_model=ROIMetrics)
async def get_roi(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Calculate Return on Investment (ROI)

    ROI shows the percentage return on the net invested amount.
    Formula: (Current Value - Net Invested) / Net Invested * 100
    """
    analytics_service = AnalyticsService(db)

    try:
        # Verify portfolio ownership
        from app.models.portfolio import Portfolio
        from sqlalchemy import select, and_

        result = await db.execute(
            select(Portfolio).where(
                and_(Portfolio.id == portfolio_id, Portfolio.deleted_at.is_(None))
            )
        )
        portfolio = result.scalar_one_or_none()

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        if portfolio.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this portfolio"
            )

        roi_metrics = await analytics_service.calculate_roi(portfolio_id)
        return ROIMetrics(**roi_metrics)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate ROI: {str(e)}")


@router.get("/portfolio/{portfolio_id}/performance", response_model=PerformanceMetrics)
async def get_performance(
    portfolio_id: int,
    end_date: Optional[date] = Query(None, description="End date for calculations"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get comprehensive performance metrics (ROI, XIRR, TWR)

    - **ROI**: Simple return on investment
    - **XIRR**: Extended Internal Rate of Return (considers timing of cash flows)
    - **TWR**: Time-Weighted Return (eliminates effect of cash flows)
    """
    analytics_service = AnalyticsService(db)

    try:
        # Verify portfolio ownership
        from app.models.portfolio import Portfolio
        from sqlalchemy import select, and_

        result = await db.execute(
            select(Portfolio).where(
                and_(Portfolio.id == portfolio_id, Portfolio.deleted_at.is_(None))
            )
        )
        portfolio = result.scalar_one_or_none()

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        if portfolio.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this portfolio"
            )

        roi_metrics = await analytics_service.calculate_roi(portfolio_id)
        xirr = await analytics_service.calculate_xirr(portfolio_id, end_date)
        twr = await analytics_service.calculate_twr(portfolio_id, end_date)

        return PerformanceMetrics(
            portfolio_id=portfolio_id,
            roi=ROIMetrics(**roi_metrics),
            xirr=xirr,
            twr=twr,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to calculate performance: {str(e)}"
        )


@router.get("/portfolio/{portfolio_id}/allocation", response_model=AssetAllocation)
async def get_allocation(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get asset allocation breakdown

    Returns allocation by:
    - Asset class (equity, fixed_income, crypto, etc.)
    - Asset type (stock, ETF, bond, etc.)
    - Individual assets
    """
    analytics_service = AnalyticsService(db)

    try:
        # Verify portfolio ownership
        from app.models.portfolio import Portfolio
        from sqlalchemy import select, and_

        result = await db.execute(
            select(Portfolio).where(
                and_(Portfolio.id == portfolio_id, Portfolio.deleted_at.is_(None))
            )
        )
        portfolio = result.scalar_one_or_none()

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        if portfolio.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this portfolio"
            )

        allocation = await analytics_service.get_asset_allocation(portfolio_id)
        return AssetAllocation(**allocation)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get allocation: {str(e)}"
        )


@router.get("/portfolio/{portfolio_id}/holdings", response_model=list[HoldingPerformance])
async def get_holdings_performance(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get gain/loss for each holding

    Shows performance metrics for each individual holding including:
    - Cost basis and current value
    - Unrealized gains/losses (amount and percentage)
    - Current price and quantity
    """
    analytics_service = AnalyticsService(db)

    try:
        # Verify portfolio ownership
        from app.models.portfolio import Portfolio
        from sqlalchemy import select, and_

        result = await db.execute(
            select(Portfolio).where(
                and_(Portfolio.id == portfolio_id, Portfolio.deleted_at.is_(None))
            )
        )
        portfolio = result.scalar_one_or_none()

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        if portfolio.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this portfolio"
            )

        holdings = await analytics_service.get_holdings_performance(portfolio_id)
        return [HoldingPerformance(**h) for h in holdings]

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get holdings performance: {str(e)}"
        )


@router.get("/portfolio/{portfolio_id}/dividends", response_model=DividendMetrics)
async def get_dividend_metrics(
    portfolio_id: int,
    start_date: Optional[date] = Query(None, description="Start date for dividend tracking"),
    end_date: Optional[date] = Query(None, description="End date for dividend tracking"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get dividend tracking and yield metrics

    Returns:
    - Total dividends received in the period
    - Dividend yield (percentage)
    - Annualized dividend yield
    - Breakdown by asset
    - Payment history
    """
    analytics_service = AnalyticsService(db)

    try:
        # Verify portfolio ownership
        from app.models.portfolio import Portfolio
        from sqlalchemy import select, and_

        result = await db.execute(
            select(Portfolio).where(
                and_(Portfolio.id == portfolio_id, Portfolio.deleted_at.is_(None))
            )
        )
        portfolio = result.scalar_one_or_none()

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        if portfolio.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this portfolio"
            )

        dividends = await analytics_service.get_dividend_metrics(
            portfolio_id, start_date, end_date
        )
        return DividendMetrics(**dividends)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get dividend metrics: {str(e)}"
        )


@router.get("/portfolio/{portfolio_id}/comprehensive", response_model=ComprehensiveAnalytics)
async def get_comprehensive_analytics(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get all analytics in a single call

    Returns comprehensive portfolio analytics including:
    - Total value
    - Performance metrics (ROI, XIRR, TWR)
    - Asset allocation
    - Holdings performance
    - Dividend metrics

    This is the most complete analytics endpoint but may be slower than individual endpoints.
    """
    analytics_service = AnalyticsService(db)

    try:
        # Verify portfolio ownership first
        from app.models.portfolio import Portfolio
        from sqlalchemy import select, and_

        result = await db.execute(
            select(Portfolio).where(
                and_(Portfolio.id == portfolio_id, Portfolio.deleted_at.is_(None))
            )
        )
        portfolio = result.scalar_one_or_none()

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        if portfolio.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this portfolio"
            )

        analytics = await analytics_service.get_comprehensive_analytics(portfolio_id)
        return ComprehensiveAnalytics(**analytics)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get comprehensive analytics: {str(e)}"
        )
