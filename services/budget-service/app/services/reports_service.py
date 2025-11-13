"""
Reports service layer for analytics and reporting.

Handles generation of various financial reports and analytics.
"""

from typing import Dict, Optional
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from dateutil.relativedelta import relativedelta

from app.models.transaction import Transaction
from app.models.account import Account
from app.models.category import Category


class ReportsService:
    """Service for generating financial reports and analytics."""

    @staticmethod
    async def generate_cashflow_report(
        db: AsyncSession,
        user_id: int,
        start_date: date,
        end_date: date,
        currency: Optional[str] = None,
    ) -> Dict:
        """
        Generate monthly cashflow report.

        Args:
            db: Database session
            user_id: User ID
            start_date: Report start date
            end_date: Report end date
            currency: Optional currency filter

        Returns:
            Dictionary with cashflow report data
        """
        # Build base query filters
        filters = [
            Transaction.user_id == user_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.deleted_at.is_(None),
            Transaction.type != "transfer",  # Exclude transfers
        ]

        if currency:
            filters.append(Transaction.currency == currency.upper())

        # Determine primary currency
        if not currency:
            # Get the most common currency from user's transactions
            currency_query = (
                select(Transaction.currency)
                .filter(and_(*filters))
                .group_by(Transaction.currency)
                .order_by(func.count(Transaction.id).desc())
                .limit(1)
            )
            result = await db.execute(currency_query)
            primary_currency = result.scalar_one_or_none()
            if not primary_currency:
                primary_currency = "USD"
        else:
            primary_currency = currency.upper()

        # Query monthly cashflow data
        # Group by year-month and transaction type
        query = select(
            func.to_char(Transaction.date, "YYYY-MM").label("month"),
            Transaction.type,
            func.sum(Transaction.amount).label("total"),
        ).filter(and_(*filters))

        if currency:
            query = query.filter(Transaction.currency == currency.upper())

        query = query.group_by("month", Transaction.type).order_by("month")

        result = await db.execute(query)
        rows = result.all()

        # Organize data by month
        monthly_data: Dict[str, Dict] = {}
        for row in rows:
            month = row.month
            if month not in monthly_data:
                monthly_data[month] = {
                    "month": month,
                    "income": Decimal("0"),
                    "expenses": Decimal("0"),
                    "currency": primary_currency,
                }

            if row.type == "income":
                monthly_data[month]["income"] = Decimal(str(row.total))
            elif row.type == "expense":
                monthly_data[month]["expenses"] = Decimal(str(row.total))

        # Fill in missing months with zeros
        current = start_date.replace(day=1)
        end_month = end_date.replace(day=1)
        while current <= end_month:
            month_key = current.strftime("%Y-%m")
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    "month": month_key,
                    "income": Decimal("0"),
                    "expenses": Decimal("0"),
                    "currency": primary_currency,
                }
            current = current + relativedelta(months=1)

        # Calculate net for each month and sort
        cashflow_data = []
        total_income = Decimal("0")
        total_expenses = Decimal("0")

        for month_key in sorted(monthly_data.keys()):
            month_data = monthly_data[month_key]
            net = month_data["income"] - month_data["expenses"]
            month_data["net"] = net
            cashflow_data.append(month_data)
            total_income += month_data["income"]
            total_expenses += month_data["expenses"]

        return {
            "start_date": start_date,
            "end_date": end_date,
            "currency": primary_currency,
            "data": cashflow_data,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_cashflow": total_income - total_expenses,
        }

    @staticmethod
    async def generate_spending_report(
        db: AsyncSession,
        user_id: int,
        start_date: date,
        end_date: date,
        currency: Optional[str] = None,
    ) -> Dict:
        """
        Generate spending analysis by category.

        Args:
            db: Database session
            user_id: User ID
            start_date: Report start date
            end_date: Report end date
            currency: Optional currency filter

        Returns:
            Dictionary with spending report data
        """
        # Build base query filters
        filters = [
            Transaction.user_id == user_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.deleted_at.is_(None),
            Transaction.type == "expense",  # Only expenses
        ]

        if currency:
            filters.append(Transaction.currency == currency.upper())

        # Determine primary currency
        if not currency:
            currency_query = (
                select(Transaction.currency)
                .filter(and_(*filters))
                .group_by(Transaction.currency)
                .order_by(func.count(Transaction.id).desc())
                .limit(1)
            )
            result = await db.execute(currency_query)
            primary_currency = result.scalar_one_or_none()
            if not primary_currency:
                primary_currency = "USD"
        else:
            primary_currency = currency.upper()

        # Query spending by category
        query = (
            select(
                Transaction.category_id,
                Category.name.label("category_name"),
                func.sum(Transaction.amount).label("total_amount"),
                func.count(Transaction.id).label("transaction_count"),
            )
            .outerjoin(Category, Transaction.category_id == Category.id)
            .filter(and_(*filters))
            .group_by(Transaction.category_id, Category.name)
            .order_by(func.sum(Transaction.amount).desc())
        )

        result = await db.execute(query)
        rows = result.all()

        # Calculate total spending
        total_spending = sum(Decimal(str(row.total_amount)) for row in rows)
        total_transactions = sum(row.transaction_count for row in rows)

        # Build category breakdown
        categories = []
        for row in rows:
            amount = Decimal(str(row.total_amount))
            percentage = (
                (amount / total_spending * 100) if total_spending > 0 else Decimal("0")
            )
            categories.append({
                "category_id": row.category_id,
                "category_name": row.category_name or "Uncategorized",
                "total_amount": amount,
                "transaction_count": row.transaction_count,
                "percentage": round(percentage, 2),
            })

        return {
            "start_date": start_date,
            "end_date": end_date,
            "currency": primary_currency,
            "categories": categories,
            "total_spending": total_spending,
            "total_transactions": total_transactions,
        }

    @staticmethod
    async def generate_income_report(
        db: AsyncSession,
        user_id: int,
        start_date: date,
        end_date: date,
        currency: Optional[str] = None,
    ) -> Dict:
        """
        Generate income analysis report.

        Args:
            db: Database session
            user_id: User ID
            start_date: Report start date
            end_date: Report end date
            currency: Optional currency filter

        Returns:
            Dictionary with income report data
        """
        # Build base query filters
        filters = [
            Transaction.user_id == user_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.deleted_at.is_(None),
            Transaction.type == "income",  # Only income
        ]

        if currency:
            filters.append(Transaction.currency == currency.upper())

        # Determine primary currency
        if not currency:
            currency_query = (
                select(Transaction.currency)
                .filter(and_(*filters))
                .group_by(Transaction.currency)
                .order_by(func.count(Transaction.id).desc())
                .limit(1)
            )
            result = await db.execute(currency_query)
            primary_currency = result.scalar_one_or_none()
            if not primary_currency:
                primary_currency = "USD"
        else:
            primary_currency = currency.upper()

        # Query income by category
        query = (
            select(
                Transaction.category_id,
                Category.name.label("category_name"),
                func.sum(Transaction.amount).label("total_amount"),
                func.count(Transaction.id).label("transaction_count"),
            )
            .outerjoin(Category, Transaction.category_id == Category.id)
            .filter(and_(*filters))
            .group_by(Transaction.category_id, Category.name)
            .order_by(func.sum(Transaction.amount).desc())
        )

        result = await db.execute(query)
        rows = result.all()

        # Calculate total income
        total_income = sum(Decimal(str(row.total_amount)) for row in rows)
        total_transactions = sum(row.transaction_count for row in rows)

        # Build income sources breakdown
        sources = []
        for row in rows:
            amount = Decimal(str(row.total_amount))
            percentage = (
                (amount / total_income * 100) if total_income > 0 else Decimal("0")
            )
            sources.append({
                "category_id": row.category_id,
                "category_name": row.category_name or "Uncategorized",
                "total_amount": amount,
                "transaction_count": row.transaction_count,
                "percentage": round(percentage, 2),
            })

        # Calculate average monthly income
        months_count = (
            (end_date.year - start_date.year) * 12
            + (end_date.month - start_date.month)
            + 1
        )
        average_monthly_income = (
            total_income / months_count if months_count > 0 else Decimal("0")
        )

        return {
            "start_date": start_date,
            "end_date": end_date,
            "currency": primary_currency,
            "sources": sources,
            "total_income": total_income,
            "total_transactions": total_transactions,
            "average_monthly_income": round(average_monthly_income, 2),
        }

    @staticmethod
    async def generate_net_worth_report(
        db: AsyncSession,
        user_id: int,
        start_date: date,
        end_date: date,
        currency: Optional[str] = None,
    ) -> Dict:
        """
        Generate net worth timeline report.

        Args:
            db: Database session
            user_id: User ID
            start_date: Report start date
            end_date: Report end date
            currency: Optional currency filter

        Returns:
            Dictionary with net worth report data
        """
        # Determine primary currency
        if not currency:
            # Get the most common currency from user's accounts
            currency_query = (
                select(Account.currency)
                .filter(
                    and_(
                        Account.user_id == user_id,
                        Account.deleted_at.is_(None),
                        Account.include_in_net_worth.is_(True),
                    )
                )
                .group_by(Account.currency)
                .order_by(func.count(Account.id).desc())
                .limit(1)
            )
            result = await db.execute(currency_query)
            primary_currency = result.scalar_one_or_none()
            if not primary_currency:
                primary_currency = "USD"
        else:
            primary_currency = currency.upper()

        # Get current account balances
        accounts_query = select(Account).filter(
            and_(
                Account.user_id == user_id,
                Account.deleted_at.is_(None),
                Account.include_in_net_worth.is_(True),
            )
        )

        if currency:
            accounts_query = accounts_query.filter(Account.currency == currency.upper())

        result = await db.execute(accounts_query)
        accounts = result.scalars().all()

        # Build current account balances
        current_accounts = []
        current_assets = Decimal("0")
        current_liabilities = Decimal("0")

        for account in accounts:
            current_accounts.append({
                "account_id": account.id,
                "account_name": account.name,
                "account_type": account.type,
                "balance": account.current_balance,
                "currency": account.currency,
            })

            if account.current_balance >= 0:
                current_assets += account.current_balance
            else:
                current_liabilities += abs(account.current_balance)

        current_net_worth = current_assets - current_liabilities

        # Calculate historical net worth at monthly intervals
        # For simplicity, we'll calculate net worth at the beginning of each month
        # by reconstructing account balances from transactions
        timeline = []
        current = start_date.replace(day=1)
        end_month = end_date.replace(day=1)

        while current <= end_month:
            # Calculate net worth at this point
            # This is a simplified calculation - in production, you'd want to store
            # historical balances or calculate them more accurately
            snapshot_date = current

            # For the current month, use actual current balances
            if current.year == date.today().year and current.month == date.today().month:
                net_worth = current_net_worth
                assets = current_assets
                liabilities = current_liabilities
            else:
                # For historical months, we'll use a simplified calculation
                # Calculate balance at that point by working backwards from current balance
                # This is approximate and assumes we're tracking from the start
                assets = Decimal("0")
                liabilities = Decimal("0")

                for account in accounts:
                    # Calculate transactions from snapshot_date to now
                    trans_query = select(func.sum(Transaction.amount)).filter(
                        and_(
                            Transaction.account_id == account.id,
                            Transaction.date > snapshot_date,
                            Transaction.deleted_at.is_(None),
                        )
                    )
                    result = await db.execute(trans_query)
                    future_transactions = result.scalar_one_or_none() or 0

                    # Estimated balance at snapshot date
                    estimated_balance = account.current_balance - Decimal(
                        str(future_transactions)
                    )

                    if estimated_balance >= 0:
                        assets += estimated_balance
                    else:
                        liabilities += abs(estimated_balance)

                net_worth = assets - liabilities

            timeline.append({
                "date": snapshot_date,
                "total_assets": assets,
                "total_liabilities": liabilities,
                "net_worth": net_worth,
                "currency": primary_currency,
            })

            current = current + relativedelta(months=1)

        # Calculate change
        if len(timeline) > 1:
            start_net_worth = timeline[0]["net_worth"]
            change = current_net_worth - start_net_worth
            change_percentage = (
                (change / abs(start_net_worth) * 100)
                if start_net_worth != 0
                else Decimal("0")
            )
        else:
            change = Decimal("0")
            change_percentage = Decimal("0")

        return {
            "start_date": start_date,
            "end_date": end_date,
            "currency": primary_currency,
            "timeline": timeline,
            "current_net_worth": current_net_worth,
            "change": change,
            "change_percentage": round(change_percentage, 2),
            "accounts": current_accounts,
        }
