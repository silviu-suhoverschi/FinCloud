"""
Budget service layer for business logic.

Handles budget creation, updates, and spending calculations.
"""

from typing import Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.budget import Budget
from app.models.category import Category
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.budget_spending_cache import BudgetSpendingCache


class BudgetService:
    """Service for managing budgets and spending calculations."""

    @staticmethod
    async def validate_budget_data(
        db: AsyncSession,
        user_id: int,
        category_id: Optional[int] = None,
        account_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        budget_id: Optional[int] = None,
    ) -> None:
        """
        Validate budget data.

        Args:
            db: Database session
            user_id: User ID
            category_id: Category ID (optional)
            account_id: Account ID (optional)
            start_date: Budget start date
            end_date: Budget end date
            budget_id: Current budget ID (for updates, to exclude self)

        Raises:
            ValueError: If validation fails
        """
        # Validate that at least one of category_id or account_id is provided
        if category_id is None and account_id is None:
            raise ValueError("Either category_id or account_id must be provided")

        # Validate category exists and belongs to user
        if category_id is not None:
            category_query = select(Category).filter(
                and_(
                    Category.id == category_id,
                    Category.user_id == user_id,
                    Category.deleted_at.is_(None),
                )
            )
            result = await db.execute(category_query)
            category = result.scalar_one_or_none()

            if not category:
                raise ValueError(
                    f"Category with ID {category_id} not found or does not belong to user"
                )

        # Validate account exists and belongs to user
        if account_id is not None:
            account_query = select(Account).filter(
                and_(
                    Account.id == account_id,
                    Account.user_id == user_id,
                    Account.deleted_at.is_(None),
                )
            )
            result = await db.execute(account_query)
            account = result.scalar_one_or_none()

            if not account:
                raise ValueError(
                    f"Account with ID {account_id} not found or does not belong to user"
                )

        # Validate date range
        if start_date and end_date:
            if end_date < start_date:
                raise ValueError("End date must be after start date")

    @staticmethod
    async def calculate_budget_spending(
        db: AsyncSession,
        budget: Budget,
        current_date: Optional[date] = None,
    ) -> dict:
        """
        Calculate spending for a budget.

        Args:
            db: Database session
            budget: Budget model instance
            current_date: Current date for calculations (defaults to today)

        Returns:
            Dictionary with spending information
        """
        if current_date is None:
            current_date = date.today()

        # Determine the period dates
        period_start, period_end = BudgetService._calculate_period_dates(
            budget.period, budget.start_date, budget.end_date, current_date
        )

        # Try to get from cache first
        cache_query = select(BudgetSpendingCache).filter(
            and_(
                BudgetSpendingCache.budget_id == budget.id,
                BudgetSpendingCache.period_start == period_start,
                BudgetSpendingCache.period_end == period_end,
            )
        )
        cache_result = await db.execute(cache_query)
        cache = cache_result.scalar_one_or_none()

        # If cache exists and is recent (less than 1 hour old), use it
        if cache and (datetime.utcnow() - cache.last_calculated_at) < timedelta(
            hours=1
        ):
            total_spent = cache.total_spent
            transaction_count = cache.transaction_count
        else:
            # Calculate from transactions
            total_spent, transaction_count = (
                await BudgetService._calculate_spending_from_transactions(
                    db, budget, period_start, period_end
                )
            )

            # Update or create cache
            if cache:
                cache.total_spent = total_spent
                cache.transaction_count = transaction_count
                cache.last_calculated_at = datetime.utcnow()
            else:
                cache = BudgetSpendingCache(
                    budget_id=budget.id,
                    period_start=period_start,
                    period_end=period_end,
                    total_spent=total_spent,
                    total_budget=budget.amount,
                    transaction_count=transaction_count,
                    last_calculated_at=datetime.utcnow(),
                )
                db.add(cache)

            # Commit cache update
            await db.commit()

        # Calculate derived values
        remaining = budget.amount - total_spent
        percentage_used = (
            (total_spent / budget.amount * 100) if budget.amount > 0 else Decimal("0")
        )
        is_over_budget = total_spent > budget.amount

        # Calculate days remaining
        days_remaining = None
        if period_end:
            days_remaining = max(0, (period_end - current_date).days)

        return {
            "total_spent": total_spent,
            "remaining": remaining,
            "percentage_used": round(percentage_used, 2),
            "transaction_count": transaction_count,
            "is_over_budget": is_over_budget,
            "days_remaining": days_remaining,
        }

    @staticmethod
    async def _calculate_spending_from_transactions(
        db: AsyncSession,
        budget: Budget,
        period_start: date,
        period_end: date,
    ) -> Tuple[Decimal, int]:
        """
        Calculate spending from transactions for a budget period.

        Args:
            db: Database session
            budget: Budget model instance
            period_start: Period start date
            period_end: Period end date

        Returns:
            Tuple of (total_spent, transaction_count)
        """
        # Build query filters
        filters = [
            Transaction.user_id == budget.user_id,
            Transaction.date >= period_start,
            Transaction.date <= period_end,
            Transaction.deleted_at.is_(None),
        ]

        # Filter by category or account
        if budget.category_id is not None:
            filters.append(Transaction.category_id == budget.category_id)
        if budget.account_id is not None:
            filters.append(Transaction.account_id == budget.account_id)

        # Calculate total spending (only count expenses, not income)
        filters.append(Transaction.type == "expense")  # Only expenses

        query = select(
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
            func.count(Transaction.id).label("count"),
        ).filter(and_(*filters))

        result = await db.execute(query)
        row = result.one()

        # Total spent from expense transactions (amounts are already positive)
        total_spent = Decimal(str(row.total))
        transaction_count = row.count

        return total_spent, transaction_count

    @staticmethod
    def _calculate_period_dates(
        period: str,
        start_date: date,
        end_date: Optional[date],
        current_date: date,
    ) -> Tuple[date, date]:
        """
        Calculate the current period dates based on budget period type.

        Args:
            period: Budget period type
            start_date: Budget start date
            end_date: Budget end date (for custom periods)
            current_date: Current date

        Returns:
            Tuple of (period_start, period_end)
        """
        if period == "custom":
            return start_date, end_date or current_date

        # Calculate how many periods have passed since start_date
        days_since_start = (current_date - start_date).days

        if period == "daily":
            period_start = current_date
            period_end = current_date
        elif period == "weekly":
            weeks_passed = days_since_start // 7
            period_start = start_date + timedelta(weeks=weeks_passed)
            period_end = period_start + timedelta(days=6)
        elif period == "monthly":
            # Calculate months passed
            months_passed = (
                (current_date.year - start_date.year) * 12
                + current_date.month
                - start_date.month
            )
            year = start_date.year + (start_date.month + months_passed - 1) // 12
            month = (start_date.month + months_passed - 1) % 12 + 1

            period_start = date(year, month, start_date.day)

            # Calculate end of month
            if month == 12:
                next_month = date(year + 1, 1, 1)
            else:
                next_month = date(year, month + 1, 1)
            period_end = next_month - timedelta(days=1)
        elif period == "quarterly":
            quarters_passed = days_since_start // 91  # Approximate
            period_start = start_date + timedelta(days=quarters_passed * 91)
            period_end = period_start + timedelta(days=90)
        elif period == "yearly":
            years_passed = current_date.year - start_date.year
            period_start = date(
                start_date.year + years_passed, start_date.month, start_date.day
            )
            period_end = date(
                start_date.year + years_passed + 1, start_date.month, start_date.day
            ) - timedelta(days=1)
        else:
            period_start = start_date
            period_end = end_date or current_date

        return period_start, period_end

    @staticmethod
    async def get_budget_progress(
        db: AsyncSession,
        budget: Budget,
        current_date: Optional[date] = None,
    ) -> dict:
        """
        Get detailed progress information for a budget.

        Args:
            db: Database session
            budget: Budget model instance
            current_date: Current date for calculations

        Returns:
            Dictionary with progress information
        """
        spending_info = await BudgetService.calculate_budget_spending(
            db, budget, current_date
        )

        # Determine if alert should be triggered
        should_alert = (
            budget.alert_enabled
            and spending_info["percentage_used"] >= budget.alert_threshold
        )

        # Get period dates
        if current_date is None:
            current_date = date.today()

        period_start, period_end = BudgetService._calculate_period_dates(
            budget.period, budget.start_date, budget.end_date, current_date
        )

        return {
            "budget_id": budget.id,
            "budget_name": budget.name,
            "amount": budget.amount,
            "currency": budget.currency,
            "period": budget.period,
            "start_date": period_start,
            "end_date": period_end,
            "total_spent": spending_info["total_spent"],
            "remaining": spending_info["remaining"],
            "percentage_used": spending_info["percentage_used"],
            "transaction_count": spending_info["transaction_count"],
            "is_over_budget": spending_info["is_over_budget"],
            "days_remaining": spending_info["days_remaining"],
            "alert_threshold": budget.alert_threshold,
            "should_alert": should_alert,
        }
