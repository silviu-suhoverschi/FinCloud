"""
Analytics service for portfolio performance calculations

Implements:
- Portfolio total value
- ROI (Return on Investment)
- XIRR (Extended Internal Rate of Return)
- TWR (Time-Weighted Return)
- Asset allocation breakdown
- Gain/loss per holding
- Dividend tracking and yield
"""

import logging
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from scipy import optimize

from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.models.portfolio_transaction import PortfolioTransaction
from app.models.asset import Asset

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for portfolio analytics and performance calculations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_portfolio_total_value(self, portfolio_id: int) -> Decimal:
        """
        Calculate total portfolio value based on current holdings and prices

        Args:
            portfolio_id: Portfolio ID

        Returns:
            Total portfolio value
        """
        result = await self.db.execute(
            select(Holding)
            .where(
                and_(
                    Holding.portfolio_id == portfolio_id,
                    Holding.deleted_at.is_(None),
                    Holding.quantity > 0,
                )
            )
        )
        holdings = result.scalars().all()

        total_value = Decimal("0")
        for holding in holdings:
            if holding.current_value:
                total_value += holding.current_value
            elif holding.current_price and holding.quantity:
                total_value += holding.current_price * holding.quantity

        return total_value

    async def calculate_roi(self, portfolio_id: int) -> Dict[str, Decimal]:
        """
        Calculate Return on Investment (ROI)

        ROI = (Current Value - Total Invested) / Total Invested * 100

        Args:
            portfolio_id: Portfolio ID

        Returns:
            Dictionary with ROI metrics
        """
        # Get current portfolio value
        current_value = await self.get_portfolio_total_value(portfolio_id)

        # Get total invested (sum of all BUY transactions minus SELL transactions)
        result = await self.db.execute(
            select(PortfolioTransaction)
            .where(
                and_(
                    PortfolioTransaction.portfolio_id == portfolio_id,
                    PortfolioTransaction.deleted_at.is_(None),
                )
            )
        )
        transactions = result.scalars().all()

        total_invested = Decimal("0")
        total_withdrawn = Decimal("0")

        for txn in transactions:
            if txn.type == "buy":
                total_invested += txn.total_amount + txn.fee + txn.tax
            elif txn.type == "sell":
                total_withdrawn += txn.total_amount - txn.fee - txn.tax
            elif txn.type == "transfer_in":
                total_invested += txn.total_amount

        # Net invested = total invested - total withdrawn
        net_invested = total_invested - total_withdrawn

        if net_invested == 0:
            return {
                "current_value": current_value,
                "total_invested": total_invested,
                "total_withdrawn": total_withdrawn,
                "net_invested": net_invested,
                "absolute_gain_loss": Decimal("0"),
                "roi_percent": Decimal("0"),
            }

        absolute_gain_loss = current_value - net_invested
        roi_percent = (absolute_gain_loss / net_invested) * Decimal("100")

        return {
            "current_value": current_value,
            "total_invested": total_invested,
            "total_withdrawn": total_withdrawn,
            "net_invested": net_invested,
            "absolute_gain_loss": absolute_gain_loss,
            "roi_percent": roi_percent,
        }

    async def calculate_xirr(
        self, portfolio_id: int, end_date: Optional[date] = None
    ) -> Optional[Decimal]:
        """
        Calculate Extended Internal Rate of Return (XIRR)

        XIRR considers the timing of cash flows, making it more accurate than simple ROI

        Args:
            portfolio_id: Portfolio ID
            end_date: End date for calculation (defaults to today)

        Returns:
            XIRR as a percentage or None if calculation fails
        """
        if end_date is None:
            end_date = date.today()

        # Get all transactions (cash flows)
        result = await self.db.execute(
            select(PortfolioTransaction)
            .where(
                and_(
                    PortfolioTransaction.portfolio_id == portfolio_id,
                    PortfolioTransaction.deleted_at.is_(None),
                    PortfolioTransaction.date <= end_date,
                )
            )
            .order_by(PortfolioTransaction.date)
        )
        transactions = result.scalars().all()

        if not transactions:
            return None

        # Build cash flow list
        cash_flows = []
        dates = []

        for txn in transactions:
            if txn.type == "buy" or txn.type == "transfer_in":
                # Money going out (negative)
                cash_flows.append(-float(txn.total_amount + txn.fee + txn.tax))
                dates.append(txn.date)
            elif txn.type == "sell" or txn.type == "transfer_out":
                # Money coming in (positive)
                cash_flows.append(float(txn.total_amount - txn.fee - txn.tax))
                dates.append(txn.date)
            elif txn.type == "dividend" or txn.type == "interest":
                # Income (positive)
                cash_flows.append(float(txn.total_amount - txn.tax))
                dates.append(txn.date)

        if not cash_flows:
            return None

        # Add current portfolio value as final cash flow
        current_value = await self.get_portfolio_total_value(portfolio_id)
        cash_flows.append(float(current_value))
        dates.append(end_date)

        # Convert dates to days from first transaction
        first_date = dates[0]
        days = [(d - first_date).days for d in dates]

        # Calculate XIRR using Newton's method
        try:
            # XIRR function to minimize
            def xirr_formula(rate):
                return sum(
                    cf / ((1 + rate) ** (day / 365.0)) for cf, day in zip(cash_flows, days)
                )

            # Find the rate that makes NPV = 0
            result = optimize.newton(xirr_formula, 0.1)
            xirr_percent = Decimal(str(result * 100))

            return xirr_percent

        except (RuntimeError, ValueError) as e:
            logger.warning(f"XIRR calculation failed for portfolio {portfolio_id}: {e}")
            return None

    async def calculate_twr(
        self, portfolio_id: int, end_date: Optional[date] = None
    ) -> Optional[Decimal]:
        """
        Calculate Time-Weighted Return (TWR)

        TWR eliminates the effect of cash flows, showing pure investment performance

        Args:
            portfolio_id: Portfolio ID
            end_date: End date for calculation (defaults to today)

        Returns:
            TWR as a percentage or None if calculation fails
        """
        if end_date is None:
            end_date = date.today()

        # Get all transactions in chronological order
        result = await self.db.execute(
            select(PortfolioTransaction)
            .where(
                and_(
                    PortfolioTransaction.portfolio_id == portfolio_id,
                    PortfolioTransaction.deleted_at.is_(None),
                    PortfolioTransaction.date <= end_date,
                )
            )
            .order_by(PortfolioTransaction.date)
        )
        transactions = result.scalars().all()

        if not transactions:
            return None

        # For a simplified TWR calculation:
        # TWR = (Ending Value / Beginning Value) - 1
        # For multiple periods: TWR = [(1 + R1) * (1 + R2) * ... * (1 + Rn)] - 1

        # Get the earliest transaction date
        start_date = transactions[0].date

        # Get initial investment
        initial_value = Decimal("0")
        for txn in transactions:
            if txn.date == start_date and txn.type == "buy":
                initial_value += txn.total_amount + txn.fee + txn.tax

        if initial_value == 0:
            return None

        # Get current value
        current_value = await self.get_portfolio_total_value(portfolio_id)

        # Simple TWR calculation
        twr = ((current_value / initial_value) - Decimal("1")) * Decimal("100")

        return twr

    async def get_asset_allocation(
        self, portfolio_id: int
    ) -> List[Dict[str, any]]:
        """
        Get asset allocation breakdown by asset class and type

        Args:
            portfolio_id: Portfolio ID

        Returns:
            List of allocation dictionaries
        """
        result = await self.db.execute(
            select(Holding, Asset)
            .join(Asset, Holding.asset_id == Asset.id)
            .where(
                and_(
                    Holding.portfolio_id == portfolio_id,
                    Holding.deleted_at.is_(None),
                    Holding.quantity > 0,
                )
            )
        )
        holdings_with_assets = result.all()

        # Calculate total portfolio value
        total_value = Decimal("0")
        allocation_by_class = {}
        allocation_by_type = {}
        allocation_by_asset = []

        for holding, asset in holdings_with_assets:
            value = holding.current_value or (
                holding.current_price * holding.quantity
                if holding.current_price
                else Decimal("0")
            )
            total_value += value

            # By asset class
            asset_class = asset.asset_class or "Unknown"
            if asset_class not in allocation_by_class:
                allocation_by_class[asset_class] = Decimal("0")
            allocation_by_class[asset_class] += value

            # By asset type
            asset_type = asset.type or "Unknown"
            if asset_type not in allocation_by_type:
                allocation_by_type[asset_type] = Decimal("0")
            allocation_by_type[asset_type] += value

            # Individual assets
            allocation_by_asset.append(
                {
                    "asset_id": asset.id,
                    "symbol": asset.symbol,
                    "name": asset.name,
                    "type": asset.type,
                    "asset_class": asset.asset_class,
                    "value": value,
                    "quantity": holding.quantity,
                    "percentage": Decimal("0"),  # Will calculate after total
                }
            )

        # Calculate percentages
        if total_value > 0:
            by_class = [
                {
                    "asset_class": cls,
                    "value": val,
                    "percentage": (val / total_value) * Decimal("100"),
                }
                for cls, val in allocation_by_class.items()
            ]

            by_type = [
                {
                    "asset_type": typ,
                    "value": val,
                    "percentage": (val / total_value) * Decimal("100"),
                }
                for typ, val in allocation_by_type.items()
            ]

            for asset in allocation_by_asset:
                asset["percentage"] = (asset["value"] / total_value) * Decimal("100")
        else:
            by_class = []
            by_type = []

        return {
            "total_value": total_value,
            "by_class": sorted(by_class, key=lambda x: x["value"], reverse=True),
            "by_type": sorted(by_type, key=lambda x: x["value"], reverse=True),
            "by_asset": sorted(allocation_by_asset, key=lambda x: x["value"], reverse=True),
        }

    async def get_holdings_performance(
        self, portfolio_id: int
    ) -> List[Dict[str, any]]:
        """
        Get gain/loss for each holding

        Args:
            portfolio_id: Portfolio ID

        Returns:
            List of holdings with performance metrics
        """
        result = await self.db.execute(
            select(Holding, Asset)
            .join(Asset, Holding.asset_id == Asset.id)
            .where(
                and_(
                    Holding.portfolio_id == portfolio_id,
                    Holding.deleted_at.is_(None),
                    Holding.quantity > 0,
                )
            )
        )
        holdings_with_assets = result.all()

        holdings_performance = []

        for holding, asset in holdings_with_assets:
            current_value = holding.current_value or (
                holding.current_price * holding.quantity
                if holding.current_price
                else Decimal("0")
            )

            unrealized_gain_loss = current_value - holding.cost_basis
            unrealized_gain_loss_percent = (
                (unrealized_gain_loss / holding.cost_basis) * Decimal("100")
                if holding.cost_basis > 0
                else Decimal("0")
            )

            holdings_performance.append(
                {
                    "holding_id": holding.id,
                    "asset_id": asset.id,
                    "symbol": asset.symbol,
                    "name": asset.name,
                    "quantity": holding.quantity,
                    "average_cost": holding.average_cost,
                    "cost_basis": holding.cost_basis,
                    "current_price": holding.current_price,
                    "current_value": current_value,
                    "unrealized_gain_loss": unrealized_gain_loss,
                    "unrealized_gain_loss_percent": unrealized_gain_loss_percent,
                    "last_price_update": holding.last_price_update,
                }
            )

        return sorted(
            holdings_performance, key=lambda x: x["current_value"], reverse=True
        )

    async def get_dividend_metrics(
        self, portfolio_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> Dict[str, any]:
        """
        Get dividend tracking and yield metrics

        Args:
            portfolio_id: Portfolio ID
            start_date: Start date for dividend tracking
            end_date: End date for dividend tracking

        Returns:
            Dictionary with dividend metrics
        """
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            # Default to 1 year ago
            start_date = date(end_date.year - 1, end_date.month, end_date.day)

        # Get all dividend transactions
        result = await self.db.execute(
            select(PortfolioTransaction, Asset)
            .join(Asset, PortfolioTransaction.asset_id == Asset.id)
            .where(
                and_(
                    PortfolioTransaction.portfolio_id == portfolio_id,
                    PortfolioTransaction.type.in_(["dividend", "interest"]),
                    PortfolioTransaction.deleted_at.is_(None),
                    PortfolioTransaction.date >= start_date,
                    PortfolioTransaction.date <= end_date,
                )
            )
            .order_by(PortfolioTransaction.date.desc())
        )
        dividend_transactions = result.all()

        total_dividends = Decimal("0")
        dividends_by_asset = {}
        dividend_history = []

        for txn, asset in dividend_transactions:
            net_dividend = txn.total_amount - txn.tax
            total_dividends += net_dividend

            # Group by asset
            if asset.id not in dividends_by_asset:
                dividends_by_asset[asset.id] = {
                    "asset_id": asset.id,
                    "symbol": asset.symbol,
                    "name": asset.name,
                    "total_dividends": Decimal("0"),
                    "count": 0,
                }

            dividends_by_asset[asset.id]["total_dividends"] += net_dividend
            dividends_by_asset[asset.id]["count"] += 1

            dividend_history.append(
                {
                    "date": txn.date,
                    "asset_id": asset.id,
                    "symbol": asset.symbol,
                    "amount": net_dividend,
                    "tax": txn.tax,
                    "type": txn.type,
                }
            )

        # Calculate dividend yield
        current_value = await self.get_portfolio_total_value(portfolio_id)
        dividend_yield = (
            (total_dividends / current_value) * Decimal("100")
            if current_value > 0
            else Decimal("0")
        )

        # Annualize if period is not exactly 1 year
        days_in_period = (end_date - start_date).days
        if days_in_period > 0 and days_in_period != 365:
            annualization_factor = Decimal("365") / Decimal(str(days_in_period))
            annualized_yield = dividend_yield * annualization_factor
        else:
            annualized_yield = dividend_yield

        return {
            "period_start": start_date,
            "period_end": end_date,
            "total_dividends": total_dividends,
            "dividend_count": len(dividend_history),
            "dividend_yield": dividend_yield,
            "annualized_yield": annualized_yield,
            "by_asset": list(dividends_by_asset.values()),
            "history": dividend_history,
        }

    async def get_comprehensive_analytics(
        self, portfolio_id: int
    ) -> Dict[str, any]:
        """
        Get all analytics in a single call

        Args:
            portfolio_id: Portfolio ID

        Returns:
            Dictionary with all analytics
        """
        # Verify portfolio exists
        result = await self.db.execute(
            select(Portfolio).where(
                and_(
                    Portfolio.id == portfolio_id, Portfolio.deleted_at.is_(None)
                )
            )
        )
        portfolio = result.scalar_one_or_none()

        if not portfolio:
            raise ValueError(f"Portfolio {portfolio_id} not found")

        # Calculate all metrics
        total_value = await self.get_portfolio_total_value(portfolio_id)
        roi_metrics = await self.calculate_roi(portfolio_id)
        xirr = await self.calculate_xirr(portfolio_id)
        twr = await self.calculate_twr(portfolio_id)
        allocation = await self.get_asset_allocation(portfolio_id)
        holdings_performance = await self.get_holdings_performance(portfolio_id)
        dividend_metrics = await self.get_dividend_metrics(portfolio_id)

        return {
            "portfolio_id": portfolio_id,
            "portfolio_name": portfolio.name,
            "currency": portfolio.currency,
            "total_value": total_value,
            "roi": roi_metrics,
            "xirr": xirr,
            "twr": twr,
            "allocation": allocation,
            "holdings": holdings_performance,
            "dividends": dividend_metrics,
            "last_updated": datetime.now(timezone.utc),
        }
