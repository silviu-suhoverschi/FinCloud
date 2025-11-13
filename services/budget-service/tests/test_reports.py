"""
Tests for reports endpoints
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from datetime import date, timedelta
from decimal import Decimal

from app.models.user import User
from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user"""
    user = User(
        email="test_reports@example.com",
        password_hash=get_password_hash("TestPassword123"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def auth_headers(client: AsyncClient, test_user: User) -> dict:
    """Get authentication headers"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test_reports@example.com",
            "password": "TestPassword123",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(scope="function")
async def test_account(db_session: AsyncSession, test_user: User) -> Account:
    """Create a test account"""
    account = Account(
        user_id=test_user.id,
        name="Test Checking Account",
        type="checking",
        currency="USD",
        initial_balance=Decimal("5000.00"),
        current_balance=Decimal("5000.00"),
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest_asyncio.fixture(scope="function")
async def test_categories(db_session: AsyncSession, test_user: User) -> dict:
    """Create test categories"""
    income_cat = Category(
        user_id=test_user.id,
        name="Salary",
        type="income",
    )
    expense_cat_1 = Category(
        user_id=test_user.id,
        name="Groceries",
        type="expense",
    )
    expense_cat_2 = Category(
        user_id=test_user.id,
        name="Utilities",
        type="expense",
    )
    db_session.add_all([income_cat, expense_cat_1, expense_cat_2])
    await db_session.commit()
    await db_session.refresh(income_cat)
    await db_session.refresh(expense_cat_1)
    await db_session.refresh(expense_cat_2)
    return {
        "income": income_cat,
        "groceries": expense_cat_1,
        "utilities": expense_cat_2,
    }


@pytest_asyncio.fixture(scope="function")
async def test_transactions(
    db_session: AsyncSession, test_user: User, test_account: Account, test_categories: dict
) -> list:
    """Create test transactions"""
    today = date.today()
    transactions = [
        # Income transactions
        Transaction(
            user_id=test_user.id,
            account_id=test_account.id,
            category_id=test_categories["income"].id,
            type="income",
            amount=Decimal("3000.00"),
            currency="USD",
            date=today - timedelta(days=60),
            description="Salary payment",
        ),
        Transaction(
            user_id=test_user.id,
            account_id=test_account.id,
            category_id=test_categories["income"].id,
            type="income",
            amount=Decimal("3000.00"),
            currency="USD",
            date=today - timedelta(days=30),
            description="Salary payment",
        ),
        Transaction(
            user_id=test_user.id,
            account_id=test_account.id,
            category_id=test_categories["income"].id,
            type="income",
            amount=Decimal("3000.00"),
            currency="USD",
            date=today - timedelta(days=5),
            description="Salary payment",
        ),
        # Expense transactions
        Transaction(
            user_id=test_user.id,
            account_id=test_account.id,
            category_id=test_categories["groceries"].id,
            type="expense",
            amount=Decimal("500.00"),
            currency="USD",
            date=today - timedelta(days=55),
            description="Grocery shopping",
        ),
        Transaction(
            user_id=test_user.id,
            account_id=test_account.id,
            category_id=test_categories["groceries"].id,
            type="expense",
            amount=Decimal("450.00"),
            currency="USD",
            date=today - timedelta(days=25),
            description="Grocery shopping",
        ),
        Transaction(
            user_id=test_user.id,
            account_id=test_account.id,
            category_id=test_categories["utilities"].id,
            type="expense",
            amount=Decimal("200.00"),
            currency="USD",
            date=today - timedelta(days=50),
            description="Electric bill",
        ),
        Transaction(
            user_id=test_user.id,
            account_id=test_account.id,
            category_id=test_categories["utilities"].id,
            type="expense",
            amount=Decimal("180.00"),
            currency="USD",
            date=today - timedelta(days=20),
            description="Electric bill",
        ),
    ]
    db_session.add_all(transactions)
    await db_session.commit()
    return transactions


@pytest.mark.asyncio
async def test_cashflow_report(
    client: AsyncClient,
    auth_headers: dict,
    test_transactions: list,
):
    """Test cashflow report endpoint"""
    today = date.today()
    start_date = today - timedelta(days=90)
    end_date = today

    response = await client.get(
        "/api/v1/reports/cashflow",
        params={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    # Verify structure
    assert "start_date" in data
    assert "end_date" in data
    assert "currency" in data
    assert "data" in data
    assert "total_income" in data
    assert "total_expenses" in data
    assert "net_cashflow" in data

    # Verify totals
    assert float(data["total_income"]) == 9000.00
    assert float(data["total_expenses"]) == 1330.00
    assert float(data["net_cashflow"]) == 7670.00

    # Verify monthly data structure
    assert len(data["data"]) > 0
    for month_data in data["data"]:
        assert "month" in month_data
        assert "income" in month_data
        assert "expenses" in month_data
        assert "net" in month_data
        assert "currency" in month_data


@pytest.mark.asyncio
async def test_cashflow_report_with_currency_filter(
    client: AsyncClient,
    auth_headers: dict,
    test_transactions: list,
):
    """Test cashflow report with currency filter"""
    today = date.today()
    start_date = today - timedelta(days=90)
    end_date = today

    response = await client.get(
        "/api/v1/reports/cashflow",
        params={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "currency": "USD",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["currency"] == "USD"


@pytest.mark.asyncio
async def test_spending_report(
    client: AsyncClient,
    auth_headers: dict,
    test_transactions: list,
):
    """Test spending report endpoint"""
    today = date.today()
    start_date = today - timedelta(days=90)
    end_date = today

    response = await client.get(
        "/api/v1/reports/spending",
        params={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    # Verify structure
    assert "start_date" in data
    assert "end_date" in data
    assert "currency" in data
    assert "categories" in data
    assert "total_spending" in data
    assert "total_transactions" in data

    # Verify totals
    assert float(data["total_spending"]) == 1330.00
    assert data["total_transactions"] == 4

    # Verify categories
    assert len(data["categories"]) > 0
    for category in data["categories"]:
        assert "category_id" in category
        assert "category_name" in category
        assert "total_amount" in category
        assert "transaction_count" in category
        assert "percentage" in category

    # Verify percentages sum to 100%
    total_percentage = sum(float(cat["percentage"]) for cat in data["categories"])
    assert abs(total_percentage - 100.0) < 0.01  # Allow small rounding errors


@pytest.mark.asyncio
async def test_income_report(
    client: AsyncClient,
    auth_headers: dict,
    test_transactions: list,
):
    """Test income report endpoint"""
    today = date.today()
    start_date = today - timedelta(days=90)
    end_date = today

    response = await client.get(
        "/api/v1/reports/income",
        params={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    # Verify structure
    assert "start_date" in data
    assert "end_date" in data
    assert "currency" in data
    assert "sources" in data
    assert "total_income" in data
    assert "total_transactions" in data
    assert "average_monthly_income" in data

    # Verify totals
    assert float(data["total_income"]) == 9000.00
    assert data["total_transactions"] == 3

    # Verify average monthly income
    assert float(data["average_monthly_income"]) > 0

    # Verify sources
    assert len(data["sources"]) > 0
    for source in data["sources"]:
        assert "category_id" in source
        assert "category_name" in source
        assert "total_amount" in source
        assert "transaction_count" in source
        assert "percentage" in source


@pytest.mark.asyncio
async def test_net_worth_report(
    client: AsyncClient,
    auth_headers: dict,
    test_account: Account,
):
    """Test net worth report endpoint"""
    today = date.today()
    start_date = today - timedelta(days=90)
    end_date = today

    response = await client.get(
        "/api/v1/reports/net-worth",
        params={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    # Verify structure
    assert "start_date" in data
    assert "end_date" in data
    assert "currency" in data
    assert "timeline" in data
    assert "current_net_worth" in data
    assert "change" in data
    assert "change_percentage" in data
    assert "accounts" in data

    # Verify current net worth
    assert float(data["current_net_worth"]) == 5000.00

    # Verify timeline
    assert len(data["timeline"]) > 0
    for snapshot in data["timeline"]:
        assert "date" in snapshot
        assert "total_assets" in snapshot
        assert "total_liabilities" in snapshot
        assert "net_worth" in snapshot
        assert "currency" in snapshot

    # Verify accounts
    assert len(data["accounts"]) > 0
    for account in data["accounts"]:
        assert "account_id" in account
        assert "account_name" in account
        assert "account_type" in account
        assert "balance" in account
        assert "currency" in account


@pytest.mark.asyncio
async def test_report_invalid_date_range(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test reports with invalid date range"""
    today = date.today()
    start_date = today
    end_date = today - timedelta(days=30)  # End before start

    response = await client.get(
        "/api/v1/reports/cashflow",
        params={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "End date must be after start date" in response.json()["detail"]


@pytest.mark.asyncio
async def test_report_unauthorized(client: AsyncClient):
    """Test reports without authentication"""
    today = date.today()
    start_date = today - timedelta(days=30)
    end_date = today

    response = await client.get(
        "/api/v1/reports/cashflow",
        params={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
    )

    assert response.status_code == 401
