"""
Pydantic schemas for portfolio analytics.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ROIMetrics(BaseModel):
    """Return on Investment metrics"""

    current_value: Decimal = Field(..., description="Current portfolio value")
    total_invested: Decimal = Field(..., description="Total amount invested")
    total_withdrawn: Decimal = Field(..., description="Total amount withdrawn")
    net_invested: Decimal = Field(..., description="Net amount invested")
    absolute_gain_loss: Decimal = Field(..., description="Absolute gain or loss")
    roi_percent: Decimal = Field(..., description="ROI percentage")

    model_config = ConfigDict(from_attributes=True)


class AssetAllocationByClass(BaseModel):
    """Asset allocation by class"""

    asset_class: str = Field(..., description="Asset class name")
    value: Decimal = Field(..., description="Total value in this class")
    percentage: Decimal = Field(..., description="Percentage of total portfolio")

    model_config = ConfigDict(from_attributes=True)


class AssetAllocationByType(BaseModel):
    """Asset allocation by type"""

    asset_type: str = Field(..., description="Asset type")
    value: Decimal = Field(..., description="Total value of this type")
    percentage: Decimal = Field(..., description="Percentage of total portfolio")

    model_config = ConfigDict(from_attributes=True)


class AssetAllocationByAsset(BaseModel):
    """Individual asset allocation"""

    asset_id: int = Field(..., description="Asset ID")
    symbol: str = Field(..., description="Asset symbol")
    name: str = Field(..., description="Asset name")
    type: str = Field(..., description="Asset type")
    asset_class: Optional[str] = Field(None, description="Asset class")
    value: Decimal = Field(..., description="Current value")
    quantity: Decimal = Field(..., description="Quantity held")
    percentage: Decimal = Field(..., description="Percentage of total portfolio")

    model_config = ConfigDict(from_attributes=True)


class AssetAllocation(BaseModel):
    """Complete asset allocation breakdown"""

    total_value: Decimal = Field(..., description="Total portfolio value")
    by_class: List[AssetAllocationByClass] = Field(
        ..., description="Allocation by asset class"
    )
    by_type: List[AssetAllocationByType] = Field(
        ..., description="Allocation by asset type"
    )
    by_asset: List[AssetAllocationByAsset] = Field(
        ..., description="Allocation by individual asset"
    )

    model_config = ConfigDict(from_attributes=True)


class HoldingPerformance(BaseModel):
    """Performance metrics for a single holding"""

    holding_id: int = Field(..., description="Holding ID")
    asset_id: int = Field(..., description="Asset ID")
    symbol: str = Field(..., description="Asset symbol")
    name: str = Field(..., description="Asset name")
    quantity: Decimal = Field(..., description="Quantity held")
    average_cost: Decimal = Field(..., description="Average cost per unit")
    cost_basis: Decimal = Field(..., description="Total cost basis")
    current_price: Optional[Decimal] = Field(None, description="Current price per unit")
    current_value: Decimal = Field(..., description="Current total value")
    unrealized_gain_loss: Decimal = Field(..., description="Unrealized gain or loss")
    unrealized_gain_loss_percent: Decimal = Field(
        ..., description="Unrealized gain/loss percentage"
    )
    last_price_update: Optional[datetime] = Field(
        None, description="Last price update timestamp"
    )

    model_config = ConfigDict(from_attributes=True)


class DividendByAsset(BaseModel):
    """Dividend summary by asset"""

    asset_id: int = Field(..., description="Asset ID")
    symbol: str = Field(..., description="Asset symbol")
    name: str = Field(..., description="Asset name")
    total_dividends: Decimal = Field(..., description="Total dividends received")
    count: int = Field(..., description="Number of dividend payments")

    model_config = ConfigDict(from_attributes=True)


class DividendHistory(BaseModel):
    """Individual dividend payment"""

    payment_date: date = Field(..., description="Payment date", alias="date")
    asset_id: int = Field(..., description="Asset ID")
    symbol: str = Field(..., description="Asset symbol")
    amount: Decimal = Field(..., description="Dividend amount (after tax)")
    tax: Decimal = Field(..., description="Tax amount")
    type: str = Field(..., description="Transaction type (dividend/interest)")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class DividendMetrics(BaseModel):
    """Dividend tracking and yield metrics"""

    period_start: date = Field(..., description="Start date of tracking period")
    period_end: date = Field(..., description="End date of tracking period")
    total_dividends: Decimal = Field(..., description="Total dividends received")
    dividend_count: int = Field(..., description="Number of dividend payments")
    dividend_yield: Decimal = Field(..., description="Dividend yield percentage")
    annualized_yield: Decimal = Field(
        ..., description="Annualized dividend yield percentage"
    )
    by_asset: List[DividendByAsset] = Field(..., description="Dividends by asset")
    history: List[DividendHistory] = Field(..., description="Dividend payment history")

    model_config = ConfigDict(from_attributes=True)


class PerformanceMetrics(BaseModel):
    """Portfolio performance metrics"""

    portfolio_id: int = Field(..., description="Portfolio ID")
    roi: ROIMetrics = Field(..., description="Return on Investment metrics")
    xirr: Optional[Decimal] = Field(
        None, description="Extended Internal Rate of Return (XIRR) percentage"
    )
    twr: Optional[Decimal] = Field(
        None, description="Time-Weighted Return (TWR) percentage"
    )

    model_config = ConfigDict(from_attributes=True)


class ComprehensiveAnalytics(BaseModel):
    """Complete portfolio analytics"""

    portfolio_id: int = Field(..., description="Portfolio ID")
    portfolio_name: str = Field(..., description="Portfolio name")
    currency: str = Field(..., description="Portfolio currency")
    total_value: Decimal = Field(..., description="Total portfolio value")
    roi: ROIMetrics = Field(..., description="Return on Investment metrics")
    xirr: Optional[Decimal] = Field(
        None, description="Extended Internal Rate of Return (XIRR) percentage"
    )
    twr: Optional[Decimal] = Field(
        None, description="Time-Weighted Return (TWR) percentage"
    )
    allocation: AssetAllocation = Field(..., description="Asset allocation breakdown")
    holdings: List[HoldingPerformance] = Field(
        ..., description="Performance by holding"
    )
    dividends: DividendMetrics = Field(..., description="Dividend metrics")
    last_updated: datetime = Field(..., description="Last calculation timestamp")

    model_config = ConfigDict(from_attributes=True)


class PortfolioValueResponse(BaseModel):
    """Simple portfolio value response"""

    portfolio_id: int = Field(..., description="Portfolio ID")
    total_value: Decimal = Field(..., description="Total portfolio value")
    currency: str = Field(..., description="Portfolio currency")

    model_config = ConfigDict(from_attributes=True)
