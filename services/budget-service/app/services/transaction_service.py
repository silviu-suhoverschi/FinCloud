"""
Transaction service layer for business logic.

Handles transaction creation, updates, and account balance management.
"""

from decimal import Decimal
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime

from app.models.transaction import Transaction
from app.models.account import Account


class TransactionService:
    """Service for managing transactions and account balances."""

    @staticmethod
    async def update_account_balance(
        db: AsyncSession,
        account_id: int,
        amount: Decimal,
        transaction_type: str,
        is_destination: bool = False,
    ) -> None:
        """
        Update account balance based on transaction.

        Args:
            db: Database session
            account_id: Account ID to update
            amount: Transaction amount
            transaction_type: Type of transaction (income, expense, transfer)
            is_destination: Whether this is a destination account in a transfer
        """
        # Get account
        query = select(Account).filter(Account.id == account_id)
        result = await db.execute(query)
        account = result.scalar_one_or_none()

        if not account:
            raise ValueError(f"Account with ID {account_id} not found")

        # Calculate balance change based on transaction type
        if transaction_type == "income":
            account.current_balance += amount
        elif transaction_type == "expense":
            account.current_balance -= amount
        elif transaction_type == "transfer":
            if is_destination:
                # Destination account receives money
                account.current_balance += amount
            else:
                # Source account loses money
                account.current_balance -= amount

        account.updated_at = datetime.utcnow()

    @staticmethod
    async def revert_account_balance(
        db: AsyncSession,
        transaction: Transaction,
    ) -> None:
        """
        Revert account balance changes from a transaction.

        Args:
            db: Database session
            transaction: Transaction to revert
        """
        # Revert source account
        await TransactionService.update_account_balance(
            db,
            transaction.account_id,
            transaction.amount,
            # Reverse the transaction type effect
            (
                "expense"
                if transaction.type == "income"
                else "income" if transaction.type == "expense" else "transfer"
            ),
            is_destination=False,
        )

        # Revert destination account for transfers
        if transaction.type == "transfer" and transaction.destination_account_id:
            await TransactionService.update_account_balance(
                db,
                transaction.destination_account_id,
                transaction.amount,
                "transfer",
                is_destination=False,  # Revert means we subtract from destination
            )

    @staticmethod
    async def validate_transaction_data(
        db: AsyncSession,
        user_id: int,
        account_id: int,
        transaction_type: str,
        destination_account_id: Optional[int] = None,
        category_id: Optional[int] = None,
    ) -> None:
        """
        Validate transaction data.

        Args:
            db: Database session
            user_id: User ID
            account_id: Source account ID
            transaction_type: Transaction type
            destination_account_id: Destination account ID (for transfers)
            category_id: Category ID

        Raises:
            ValueError: If validation fails
        """
        # Validate source account
        query = select(Account).filter(
            and_(
                Account.id == account_id,
                Account.user_id == user_id,
                Account.deleted_at.is_(None),
            )
        )
        result = await db.execute(query)
        source_account = result.scalar_one_or_none()

        if not source_account:
            raise ValueError(
                f"Account with ID {account_id} not found or does not belong to user"
            )

        # Validate transfer requirements
        if transaction_type == "transfer":
            if not destination_account_id:
                raise ValueError("Destination account is required for transfers")

            if destination_account_id == account_id:
                raise ValueError("Source and destination accounts cannot be the same")

            # Validate destination account
            query = select(Account).filter(
                and_(
                    Account.id == destination_account_id,
                    Account.user_id == user_id,
                    Account.deleted_at.is_(None),
                )
            )
            result = await db.execute(query)
            dest_account = result.scalar_one_or_none()

            if not dest_account:
                raise ValueError(
                    f"Destination account with ID {destination_account_id} not found or does not belong to user"
                )

        # Validate category if provided
        if category_id:
            from app.models.category import Category

            query = select(Category).filter(
                and_(
                    Category.id == category_id,
                    Category.user_id == user_id,
                    Category.deleted_at.is_(None),
                )
            )
            result = await db.execute(query)
            category = result.scalar_one_or_none()

            if not category:
                raise ValueError(
                    f"Category with ID {category_id} not found or does not belong to user"
                )

    @staticmethod
    async def recalculate_account_balance(
        db: AsyncSession,
        account_id: int,
    ) -> Decimal:
        """
        Recalculate account balance from initial balance and all transactions.

        Args:
            db: Database session
            account_id: Account ID

        Returns:
            Calculated balance
        """
        # Get account
        query = select(Account).filter(Account.id == account_id)
        result = await db.execute(query)
        account = result.scalar_one_or_none()

        if not account:
            raise ValueError(f"Account with ID {account_id} not found")

        # Start with initial balance
        balance = account.initial_balance

        # Get all non-deleted transactions for this account
        query = (
            select(Transaction)
            .filter(
                and_(
                    Transaction.account_id == account_id,
                    Transaction.deleted_at.is_(None),
                )
            )
            .order_by(Transaction.date)
        )
        result = await db.execute(query)
        transactions = result.scalars().all()

        # Apply each transaction
        for transaction in transactions:
            if transaction.type == "income":
                balance += transaction.amount
            elif transaction.type == "expense":
                balance -= transaction.amount
            elif transaction.type == "transfer":
                balance -= transaction.amount

        # Add transfers TO this account
        query = (
            select(Transaction)
            .filter(
                and_(
                    Transaction.destination_account_id == account_id,
                    Transaction.type == "transfer",
                    Transaction.deleted_at.is_(None),
                )
            )
            .order_by(Transaction.date)
        )
        result = await db.execute(query)
        incoming_transfers = result.scalars().all()

        for transaction in incoming_transfers:
            balance += transaction.amount

        # Update account balance
        account.current_balance = balance
        account.updated_at = datetime.utcnow()

        return balance
