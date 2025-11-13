"""
Tests for transaction endpoints
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from datetime import date
from decimal import Decimal
import io
import csv

from app.models.user import User
from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user"""
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("TestPassword123"),
        full_name="Test User",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, test_user: User) -> dict:
    """Get authentication headers"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPassword123",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_account(db_session: AsyncSession, test_user: User) -> Account:
    """Create a test account"""
    account = Account(
        user_id=test_user.id,
        name="Test Checking Account",
        type="checking",
        currency="USD",
        initial_balance=Decimal("1000.00"),
        current_balance=Decimal("1000.00"),
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest_asyncio.fixture
async def test_account_2(db_session: AsyncSession, test_user: User) -> Account:
    """Create a second test account"""
    account = Account(
        user_id=test_user.id,
        name="Test Savings Account",
        type="savings",
        currency="USD",
        initial_balance=Decimal("5000.00"),
        current_balance=Decimal("5000.00"),
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest_asyncio.fixture
async def test_category(db_session: AsyncSession, test_user: User) -> Category:
    """Create a test category"""
    category = Category(
        user_id=test_user.id,
        name="Groceries",
        type="expense",
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest.mark.asyncio
async def test_create_income_transaction(
    client: AsyncClient,
    auth_headers: dict,
    test_account: Account,
    test_category: Category,
):
    """Test creating an income transaction"""
    transaction_data = {
        "account_id": test_account.id,
        "type": "income",
        "amount": "500.00",
        "currency": "USD",
        "date": "2024-01-15",
        "description": "Salary payment",
        "category_id": test_category.id,
        "payee": "Employer Inc",
    }

    response = await client.post(
        "/api/v1/transactions/",
        json=transaction_data,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == "500.00"
    assert data["type"] == "income"
    assert data["description"] == "Salary payment"
    assert data["account_id"] == test_account.id
    assert "id" in data
    assert "uuid" in data


@pytest.mark.asyncio
async def test_create_expense_transaction(
    client: AsyncClient,
    auth_headers: dict,
    test_account: Account,
    test_category: Category,
):
    """Test creating an expense transaction"""
    transaction_data = {
        "account_id": test_account.id,
        "type": "expense",
        "amount": "150.50",
        "currency": "USD",
        "date": "2024-01-16",
        "description": "Weekly groceries",
        "category_id": test_category.id,
        "tags": ["food", "essentials"],
    }

    response = await client.post(
        "/api/v1/transactions/",
        json=transaction_data,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == "150.50"
    assert data["type"] == "expense"
    assert data["tags"] == ["food", "essentials"]


@pytest.mark.asyncio
async def test_create_transfer_transaction(
    client: AsyncClient,
    auth_headers: dict,
    test_account: Account,
    test_account_2: Account,
):
    """Test creating a transfer transaction"""
    transaction_data = {
        "account_id": test_account.id,
        "destination_account_id": test_account_2.id,
        "type": "transfer",
        "amount": "200.00",
        "currency": "USD",
        "date": "2024-01-17",
        "description": "Transfer to savings",
    }

    response = await client.post(
        "/api/v1/transactions/",
        json=transaction_data,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == "200.00"
    assert data["type"] == "transfer"
    assert data["destination_account_id"] == test_account_2.id


@pytest.mark.asyncio
async def test_create_transfer_without_destination_fails(
    client: AsyncClient,
    auth_headers: dict,
    test_account: Account,
):
    """Test that transfer without destination account fails"""
    transaction_data = {
        "account_id": test_account.id,
        "type": "transfer",
        "amount": "200.00",
        "currency": "USD",
        "date": "2024-01-17",
        "description": "Invalid transfer",
    }

    response = await client.post(
        "/api/v1/transactions/",
        json=transaction_data,
        headers=auth_headers,
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_list_transactions(
    client: AsyncClient,
    auth_headers: dict,
    test_account: Account,
    db_session: AsyncSession,
    test_user: User,
):
    """Test listing transactions"""
    # Create some test transactions
    transactions = [
        Transaction(
            user_id=test_user.id,
            account_id=test_account.id,
            type="income",
            amount=Decimal("500.00"),
            currency="USD",
            date=date(2024, 1, 15),
            description="Income 1",
        ),
        Transaction(
            user_id=test_user.id,
            account_id=test_account.id,
            type="expense",
            amount=Decimal("100.00"),
            currency="USD",
            date=date(2024, 1, 16),
            description="Expense 1",
        ),
    ]
    for t in transactions:
        db_session.add(t)
    await db_session.commit()

    response = await client.get(
        "/api/v1/transactions/",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "transactions" in data
    assert data["total"] >= 2
    assert len(data["transactions"]) >= 2


@pytest.mark.asyncio
async def test_list_transactions_with_filters(
    client: AsyncClient,
    auth_headers: dict,
    test_account: Account,
    test_category: Category,
    db_session: AsyncSession,
    test_user: User,
):
    """Test listing transactions with filters"""
    # Create test transactions
    transactions = [
        Transaction(
            user_id=test_user.id,
            account_id=test_account.id,
            type="income",
            amount=Decimal("500.00"),
            currency="USD",
            date=date(2024, 1, 15),
            description="Income",
            category_id=test_category.id,
        ),
        Transaction(
            user_id=test_user.id,
            account_id=test_account.id,
            type="expense",
            amount=Decimal("100.00"),
            currency="USD",
            date=date(2024, 1, 16),
            description="Expense",
        ),
    ]
    for t in transactions:
        db_session.add(t)
    await db_session.commit()

    # Filter by type
    response = await client.get(
        "/api/v1/transactions/?type=income",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert all(t["type"] == "income" for t in data["transactions"])

    # Filter by date range
    response = await client.get(
        "/api/v1/transactions/?date_from=2024-01-15&date_to=2024-01-15",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert all(t["date"] == "2024-01-15" for t in data["transactions"])


@pytest.mark.asyncio
async def test_get_transaction(
    client: AsyncClient,
    auth_headers: dict,
    test_account: Account,
    db_session: AsyncSession,
    test_user: User,
):
    """Test getting a single transaction"""
    transaction = Transaction(
        user_id=test_user.id,
        account_id=test_account.id,
        type="income",
        amount=Decimal("500.00"),
        currency="USD",
        date=date(2024, 1, 15),
        description="Test transaction",
    )
    db_session.add(transaction)
    await db_session.commit()
    await db_session.refresh(transaction)

    response = await client.get(
        f"/api/v1/transactions/{transaction.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == transaction.id
    assert data["description"] == "Test transaction"


@pytest.mark.asyncio
async def test_get_nonexistent_transaction(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test getting a non-existent transaction"""
    response = await client.get(
        "/api/v1/transactions/99999",
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_transaction(
    client: AsyncClient,
    auth_headers: dict,
    test_account: Account,
    db_session: AsyncSession,
    test_user: User,
):
    """Test updating a transaction"""
    transaction = Transaction(
        user_id=test_user.id,
        account_id=test_account.id,
        type="expense",
        amount=Decimal("100.00"),
        currency="USD",
        date=date(2024, 1, 15),
        description="Original description",
    )
    db_session.add(transaction)
    await db_session.commit()
    await db_session.refresh(transaction)

    update_data = {
        "description": "Updated description",
        "amount": "150.00",
    }

    response = await client.put(
        f"/api/v1/transactions/{transaction.id}",
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated description"
    assert data["amount"] == "150.00"


@pytest.mark.asyncio
async def test_delete_transaction(
    client: AsyncClient,
    auth_headers: dict,
    test_account: Account,
    db_session: AsyncSession,
    test_user: User,
):
    """Test deleting a transaction"""
    transaction = Transaction(
        user_id=test_user.id,
        account_id=test_account.id,
        type="expense",
        amount=Decimal("100.00"),
        currency="USD",
        date=date(2024, 1, 15),
        description="To be deleted",
    )
    db_session.add(transaction)
    await db_session.commit()
    await db_session.refresh(transaction)

    response = await client.delete(
        f"/api/v1/transactions/{transaction.id}",
        headers=auth_headers,
    )

    assert response.status_code == 204

    # Verify transaction is soft deleted
    response = await client.get(
        f"/api/v1/transactions/{transaction.id}",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_search_transactions(
    client: AsyncClient,
    auth_headers: dict,
    test_account: Account,
    db_session: AsyncSession,
    test_user: User,
):
    """Test searching transactions"""
    # Create test transactions
    transactions = [
        Transaction(
            user_id=test_user.id,
            account_id=test_account.id,
            type="expense",
            amount=Decimal("50.00"),
            currency="USD",
            date=date(2024, 1, 15),
            description="Coffee at Starbucks",
            payee="Starbucks",
        ),
        Transaction(
            user_id=test_user.id,
            account_id=test_account.id,
            type="expense",
            amount=Decimal("100.00"),
            currency="USD",
            date=date(2024, 1, 16),
            description="Groceries at Walmart",
            payee="Walmart",
        ),
    ]
    for t in transactions:
        db_session.add(t)
    await db_session.commit()

    # Search for "Starbucks"
    response = await client.get(
        "/api/v1/transactions/search?query=Starbucks",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(
        "Starbucks" in t["description"] or t.get("payee") == "Starbucks"
        for t in data["transactions"]
    )


@pytest.mark.asyncio
async def test_bulk_import_transactions(
    client: AsyncClient,
    auth_headers: dict,
    test_account: Account,
    test_category: Category,
):
    """Test bulk importing transactions from CSV"""
    # Create CSV content
    csv_content = io.StringIO()
    csv_writer = csv.writer(csv_content)
    csv_writer.writerow(
        [
            "account_id",
            "type",
            "amount",
            "currency",
            "date",
            "description",
            "category_id",
            "payee",
        ]
    )
    csv_writer.writerow(
        [
            test_account.id,
            "income",
            "500.00",
            "USD",
            "2024-01-15",
            "Salary",
            test_category.id,
            "Employer",
        ]
    )
    csv_writer.writerow(
        [
            test_account.id,
            "expense",
            "100.00",
            "USD",
            "2024-01-16",
            "Groceries",
            test_category.id,
            "Store",
        ]
    )

    csv_bytes = csv_content.getvalue().encode("utf-8")

    response = await client.post(
        "/api/v1/transactions/bulk",
        files={"file": ("transactions.csv", csv_bytes, "text/csv")},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["created"] == 2
    assert data["failed"] == 0
    assert len(data["transactions"]) == 2


@pytest.mark.asyncio
async def test_bulk_import_with_errors(
    client: AsyncClient,
    auth_headers: dict,
    test_account: Account,
):
    """Test bulk import with some invalid rows"""
    # Create CSV with one valid and one invalid row
    csv_content = io.StringIO()
    csv_writer = csv.writer(csv_content)
    csv_writer.writerow(
        ["account_id", "type", "amount", "currency", "date", "description"]
    )
    csv_writer.writerow(
        [test_account.id, "income", "500.00", "USD", "2024-01-15", "Valid transaction"]
    )
    csv_writer.writerow(
        [999999, "income", "500.00", "USD", "2024-01-16", "Invalid account"]
    )

    csv_bytes = csv_content.getvalue().encode("utf-8")

    response = await client.post(
        "/api/v1/transactions/bulk",
        files={"file": ("transactions.csv", csv_bytes, "text/csv")},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["created"] == 1
    assert data["failed"] == 1
    assert len(data["errors"]) == 1


@pytest.mark.asyncio
async def test_bulk_import_invalid_file_type(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test bulk import with non-CSV file"""
    response = await client.post(
        "/api/v1/transactions/bulk",
        files={"file": ("data.txt", b"not a csv", "text/plain")},
        headers=auth_headers,
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_account_balance_updates_on_transaction_create(
    client: AsyncClient,
    auth_headers: dict,
    test_account: Account,
    db_session: AsyncSession,
):
    """Test that account balance is updated when transaction is created"""
    initial_balance = test_account.current_balance

    # Create income transaction
    transaction_data = {
        "account_id": test_account.id,
        "type": "income",
        "amount": "500.00",
        "currency": "USD",
        "date": "2024-01-15",
        "description": "Income",
    }

    response = await client.post(
        "/api/v1/transactions/",
        json=transaction_data,
        headers=auth_headers,
    )

    assert response.status_code == 201

    # Refresh account to get updated balance
    await db_session.refresh(test_account)
    assert test_account.current_balance == initial_balance + Decimal("500.00")


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test that endpoints require authentication"""
    response = await client.get("/api/v1/transactions/")
    assert response.status_code == 401

    response = await client.post(
        "/api/v1/transactions/",
        json={
            "account_id": 1,
            "type": "income",
            "amount": "100.00",
            "currency": "USD",
            "date": "2024-01-15",
            "description": "Test",
        },
    )
    assert response.status_code == 401
