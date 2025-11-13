"""
Transactions API endpoints
"""

from typing import Optional, List
import csv
import io
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from datetime import datetime, date
from decimal import Decimal

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.models.account import Account
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionList,
    TransactionBulkResponse,
    TransactionType,
)
from app.services.transaction_service import TransactionService

router = APIRouter()


@router.get("/", response_model=TransactionList)
async def list_transactions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Max number of records to return"
    ),
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    type: Optional[TransactionType] = Query(
        None, description="Filter by transaction type"
    ),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    date_from: Optional[date] = Query(None, description="Filter by start date"),
    date_to: Optional[date] = Query(None, description="Filter by end date"),
    min_amount: Optional[Decimal] = Query(None, ge=0, description="Minimum amount"),
    max_amount: Optional[Decimal] = Query(None, ge=0, description="Maximum amount"),
    is_reconciled: Optional[bool] = Query(
        None, description="Filter by reconciled status"
    ),
    payee: Optional[str] = Query(None, description="Filter by payee name"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all transactions for the current user with optional filters.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **account_id**: Filter by account ID
    - **type**: Filter by transaction type (income, expense, transfer)
    - **category_id**: Filter by category ID
    - **date_from**: Filter transactions from this date
    - **date_to**: Filter transactions up to this date
    - **min_amount**: Filter transactions with amount >= this value
    - **max_amount**: Filter transactions with amount <= this value
    - **is_reconciled**: Filter by reconciled status
    - **payee**: Filter by payee name (partial match)
    """
    # Build query filters
    filters = [Transaction.user_id == current_user.id, Transaction.deleted_at.is_(None)]

    if account_id is not None:
        filters.append(
            or_(
                Transaction.account_id == account_id,
                Transaction.destination_account_id == account_id,
            )
        )

    if type is not None:
        filters.append(Transaction.type == type.value)

    if category_id is not None:
        filters.append(Transaction.category_id == category_id)

    if date_from is not None:
        filters.append(Transaction.date >= date_from)

    if date_to is not None:
        filters.append(Transaction.date <= date_to)

    if min_amount is not None:
        filters.append(Transaction.amount >= min_amount)

    if max_amount is not None:
        filters.append(Transaction.amount <= max_amount)

    if is_reconciled is not None:
        filters.append(Transaction.is_reconciled == is_reconciled)

    if payee is not None:
        filters.append(Transaction.payee.ilike(f"%{payee}%"))

    # Get total count
    count_query = select(func.count()).select_from(Transaction).filter(and_(*filters))
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Get transactions with pagination
    query = (
        select(Transaction)
        .filter(and_(*filters))
        .order_by(Transaction.date.desc(), Transaction.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    transactions = result.scalars().all()

    return TransactionList(total=total, transactions=transactions)


@router.post(
    "/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED
)
async def create_transaction(
    transaction_data: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new transaction for the current user.

    - **account_id**: Account ID for the transaction (required)
    - **type**: Transaction type - income, expense, or transfer (required)
    - **amount**: Transaction amount in the specified currency (required, must be positive)
    - **currency**: Currency code (required, ISO 4217)
    - **date**: Transaction date (required)
    - **description**: Transaction description (required)
    - **category_id**: Category ID (optional, not required for transfers)
    - **destination_account_id**: Destination account ID (required for transfers)
    - **payee**: Payee name (optional)
    - **reference_number**: Reference number (optional)
    - **notes**: Additional notes (optional)
    - **tags**: Tags for categorization (optional)
    - **exchange_rate**: Exchange rate (optional, default: 1.0)
    - **is_reconciled**: Whether transaction is reconciled (optional, default: false)
    - **external_id**: External ID from import (optional)
    - **import_source**: Source of import (optional)
    """
    # Validate transaction data
    try:
        await TransactionService.validate_transaction_data(
            db=db,
            user_id=current_user.id,
            account_id=transaction_data.account_id,
            transaction_type=transaction_data.type.value,
            destination_account_id=transaction_data.destination_account_id,
            category_id=transaction_data.category_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Create transaction instance
    transaction = Transaction(
        user_id=current_user.id,
        account_id=transaction_data.account_id,
        type=transaction_data.type.value,
        amount=transaction_data.amount,
        currency=transaction_data.currency,
        date=transaction_data.date,
        description=transaction_data.description,
        category_id=transaction_data.category_id,
        destination_account_id=transaction_data.destination_account_id,
        payee=transaction_data.payee,
        reference_number=transaction_data.reference_number,
        notes=transaction_data.notes,
        tags=transaction_data.tags,
        exchange_rate=transaction_data.exchange_rate,
        is_reconciled=transaction_data.is_reconciled,
        external_id=transaction_data.external_id,
        import_source=transaction_data.import_source,
    )

    # Update account balances
    try:
        await TransactionService.update_account_balance(
            db=db,
            account_id=transaction_data.account_id,
            amount=transaction_data.amount,
            transaction_type=transaction_data.type.value,
            is_destination=False,
        )

        # Update destination account for transfers
        if (
            transaction_data.type == TransactionType.TRANSFER
            and transaction_data.destination_account_id
        ):
            await TransactionService.update_account_balance(
                db=db,
                account_id=transaction_data.destination_account_id,
                amount=transaction_data.amount,
                transaction_type=transaction_data.type.value,
                is_destination=True,
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)

    return transaction


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get transaction details by ID.

    Returns the transaction details if it belongs to the current user.
    """
    query = select(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id,
            Transaction.deleted_at.is_(None),
        )
    )
    result = await db.execute(query)
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found",
        )

    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing transaction.

    Updates only the fields provided in the request body.
    Account balances are automatically recalculated.
    """
    # Get the transaction
    query = select(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id,
            Transaction.deleted_at.is_(None),
        )
    )
    result = await db.execute(query)
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found",
        )

    # Revert the old transaction's effect on account balances
    try:
        await TransactionService.revert_account_balance(db=db, transaction=transaction)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Update fields that were provided
    update_data = transaction_data.model_dump(exclude_unset=True)

    # Validate if critical fields are being updated
    new_account_id = update_data.get("account_id", transaction.account_id)
    new_type = update_data.get("type", transaction.type)
    new_destination_id = update_data.get(
        "destination_account_id", transaction.destination_account_id
    )
    new_category_id = update_data.get("category_id", transaction.category_id)

    if isinstance(new_type, TransactionType):
        new_type = new_type.value

    try:
        await TransactionService.validate_transaction_data(
            db=db,
            user_id=current_user.id,
            account_id=new_account_id,
            transaction_type=new_type,
            destination_account_id=new_destination_id,
            category_id=new_category_id,
        )
    except ValueError as e:
        # Reapply the old transaction to maintain consistency
        await TransactionService.update_account_balance(
            db=db,
            account_id=transaction.account_id,
            amount=transaction.amount,
            transaction_type=transaction.type,
            is_destination=False,
        )
        if transaction.type == "transfer" and transaction.destination_account_id:
            await TransactionService.update_account_balance(
                db=db,
                account_id=transaction.destination_account_id,
                amount=transaction.amount,
                transaction_type=transaction.type,
                is_destination=True,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Apply updates
    for field, value in update_data.items():
        if field == "type" and isinstance(value, TransactionType):
            setattr(transaction, field, value.value)
        else:
            setattr(transaction, field, value)

    transaction.updated_at = datetime.utcnow()

    # Apply the updated transaction's effect on account balances
    try:
        await TransactionService.update_account_balance(
            db=db,
            account_id=transaction.account_id,
            amount=transaction.amount,
            transaction_type=transaction.type,
            is_destination=False,
        )

        # Update destination account for transfers
        if transaction.type == "transfer" and transaction.destination_account_id:
            await TransactionService.update_account_balance(
                db=db,
                account_id=transaction.destination_account_id,
                amount=transaction.amount,
                transaction_type=transaction.type,
                is_destination=True,
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    await db.commit()
    await db.refresh(transaction)

    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a transaction (soft delete).

    This performs a soft delete by setting the deleted_at timestamp.
    The transaction will no longer appear in list queries but remains in the database.
    Account balances are automatically updated.
    """
    # Get the transaction
    query = select(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id,
            Transaction.deleted_at.is_(None),
        )
    )
    result = await db.execute(query)
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found",
        )

    # Revert the transaction's effect on account balances
    try:
        await TransactionService.revert_account_balance(db=db, transaction=transaction)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Soft delete by setting deleted_at timestamp
    transaction.deleted_at = datetime.utcnow()

    await db.commit()

    return None


@router.post(
    "/bulk", response_model=TransactionBulkResponse, status_code=status.HTTP_201_CREATED
)
async def bulk_create_transactions(
    file: UploadFile = File(..., description="CSV file with transactions"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Bulk import transactions from a CSV file.

    Expected CSV format:
    - account_id: Account ID (required)
    - type: Transaction type - income, expense, or transfer (required)
    - amount: Transaction amount (required)
    - currency: Currency code (required)
    - date: Transaction date in YYYY-MM-DD format (required)
    - description: Transaction description (required)
    - category_id: Category ID (optional)
    - destination_account_id: Destination account ID (optional, required for transfers)
    - payee: Payee name (optional)
    - reference_number: Reference number (optional)
    - notes: Additional notes (optional)
    - tags: Comma-separated tags (optional)
    - exchange_rate: Exchange rate (optional, default: 1.0)
    - external_id: External ID (optional)

    Returns:
    - created: Number of transactions successfully created
    - failed: Number of transactions that failed to create
    - errors: List of errors for failed transactions
    - transactions: List of successfully created transactions
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file",
        )

    # Read CSV file
    content = await file.read()
    csv_content = content.decode("utf-8")
    csv_reader = csv.DictReader(io.StringIO(csv_content))

    created_transactions = []
    errors = []
    created_count = 0
    failed_count = 0

    for idx, row in enumerate(csv_reader, start=1):
        try:
            # Parse CSV row
            account_id = int(row.get("account_id"))
            transaction_type = row.get("type", "").lower()
            amount = Decimal(row.get("amount"))
            currency = row.get("currency", "USD")
            transaction_date = datetime.strptime(row.get("date"), "%Y-%m-%d").date()
            description = row.get("description", "").strip()

            # Optional fields
            category_id = (
                int(row.get("category_id")) if row.get("category_id") else None
            )
            destination_account_id = (
                int(row.get("destination_account_id"))
                if row.get("destination_account_id")
                else None
            )
            payee = row.get("payee") or None
            reference_number = row.get("reference_number") or None
            notes = row.get("notes") or None
            tags_str = row.get("tags", "")
            tags = [tag.strip() for tag in tags_str.split(",")] if tags_str else None
            exchange_rate = Decimal(row.get("exchange_rate", "1.0"))
            external_id = row.get("external_id") or None

            # Validate transaction type
            if transaction_type not in ["income", "expense", "transfer"]:
                raise ValueError(f"Invalid transaction type: {transaction_type}")

            # Create TransactionCreate object
            transaction_data = TransactionCreate(
                account_id=account_id,
                type=TransactionType(transaction_type),
                amount=amount,
                currency=currency,
                date=transaction_date,
                description=description,
                category_id=category_id,
                destination_account_id=destination_account_id,
                payee=payee,
                reference_number=reference_number,
                notes=notes,
                tags=tags,
                exchange_rate=exchange_rate,
                is_reconciled=False,
                external_id=external_id,
                import_source="csv",
            )

            # Validate transaction data
            await TransactionService.validate_transaction_data(
                db=db,
                user_id=current_user.id,
                account_id=transaction_data.account_id,
                transaction_type=transaction_data.type.value,
                destination_account_id=transaction_data.destination_account_id,
                category_id=transaction_data.category_id,
            )

            # Create transaction
            transaction = Transaction(
                user_id=current_user.id,
                account_id=transaction_data.account_id,
                type=transaction_data.type.value,
                amount=transaction_data.amount,
                currency=transaction_data.currency,
                date=transaction_data.date,
                description=transaction_data.description,
                category_id=transaction_data.category_id,
                destination_account_id=transaction_data.destination_account_id,
                payee=transaction_data.payee,
                reference_number=transaction_data.reference_number,
                notes=transaction_data.notes,
                tags=transaction_data.tags,
                exchange_rate=transaction_data.exchange_rate,
                is_reconciled=False,
                external_id=transaction_data.external_id,
                import_source="csv",
            )

            # Update account balances
            await TransactionService.update_account_balance(
                db=db,
                account_id=transaction_data.account_id,
                amount=transaction_data.amount,
                transaction_type=transaction_data.type.value,
                is_destination=False,
            )

            if (
                transaction_data.type == TransactionType.TRANSFER
                and transaction_data.destination_account_id
            ):
                await TransactionService.update_account_balance(
                    db=db,
                    account_id=transaction_data.destination_account_id,
                    amount=transaction_data.amount,
                    transaction_type=transaction_data.type.value,
                    is_destination=True,
                )

            db.add(transaction)
            await db.flush()  # Flush to get the ID
            await db.refresh(transaction)

            created_transactions.append(transaction)
            created_count += 1

        except Exception as e:
            failed_count += 1
            errors.append(
                {
                    "row": idx,
                    "error": str(e),
                    "data": dict(row),
                }
            )

    # Commit all successful transactions
    await db.commit()

    return TransactionBulkResponse(
        created=created_count,
        failed=failed_count,
        errors=errors,
        transactions=created_transactions,
    )


@router.get("/search", response_model=TransactionList)
async def search_transactions(
    query: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Max number of records to return"
    ),
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    type: Optional[TransactionType] = Query(
        None, description="Filter by transaction type"
    ),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    date_from: Optional[date] = Query(None, description="Filter by start date"),
    date_to: Optional[date] = Query(None, description="Filter by end date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Full-text search for transactions.

    Searches in the following fields:
    - description
    - payee
    - notes
    - reference_number
    - tags

    Additional filters can be applied to narrow down the search results.
    """
    # Build base filters
    filters = [Transaction.user_id == current_user.id, Transaction.deleted_at.is_(None)]

    # Full-text search conditions
    search_conditions = [
        Transaction.description.ilike(f"%{query}%"),
        Transaction.payee.ilike(f"%{query}%"),
        Transaction.notes.ilike(f"%{query}%"),
        Transaction.reference_number.ilike(f"%{query}%"),
    ]

    # Add the search conditions with OR
    filters.append(or_(*search_conditions))

    # Additional filters
    if account_id is not None:
        filters.append(
            or_(
                Transaction.account_id == account_id,
                Transaction.destination_account_id == account_id,
            )
        )

    if type is not None:
        filters.append(Transaction.type == type.value)

    if category_id is not None:
        filters.append(Transaction.category_id == category_id)

    if date_from is not None:
        filters.append(Transaction.date >= date_from)

    if date_to is not None:
        filters.append(Transaction.date <= date_to)

    # Get total count
    count_query = select(func.count()).select_from(Transaction).filter(and_(*filters))
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Get transactions with pagination
    query_stmt = (
        select(Transaction)
        .filter(and_(*filters))
        .order_by(Transaction.date.desc(), Transaction.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query_stmt)
    transactions = result.scalars().all()

    return TransactionList(total=total, transactions=transactions)
