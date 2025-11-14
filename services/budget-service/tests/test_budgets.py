"""
Tests for budget endpoints
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from decimal import Decimal
from datetime import date, timedelta

from app.models.user import User
from app.models.account import Account
from app.models.category import Category
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user"""
    user = User(
        email="test@example.com",
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
            "email": "test@example.com",
            "password": "TestPassword123",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(scope="function")
async def test_category(db_session: AsyncSession, test_user: User) -> Category:
    """Create a test category"""
    category = Category(
        user_id=test_user.id,
        name="Groceries",
        type="expense",
        color="#FF5733",
        icon="shopping-cart",
        is_active=True,
        sort_order=0,
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest_asyncio.fixture(scope="function")
async def test_account(db_session: AsyncSession, test_user: User) -> Account:
    """Create a test account"""
    account = Account(
        user_id=test_user.id,
        name="Checking Account",
        type="checking",
        currency="USD",
        initial_balance=Decimal("1000.00"),
        current_balance=Decimal("1000.00"),
        is_active=True,
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest_asyncio.fixture(scope="function")
async def test_budget(
    db_session: AsyncSession, test_user: User, test_category: Category
) -> Budget:
    """Create a test budget"""
    budget = Budget(
        user_id=test_user.id,
        category_id=test_category.id,
        name="Monthly Groceries Budget",
        amount=Decimal("500.00"),
        currency="USD",
        period="monthly",
        start_date=date.today().replace(day=1),
        is_active=True,
    )
    db_session.add(budget)
    await db_session.commit()
    await db_session.refresh(budget)
    return budget


class TestListBudgets:
    """Tests for listing budgets"""

    @pytest.mark.asyncio
    async def test_list_budgets_empty(self, client: AsyncClient, auth_headers: dict):
        """Test listing budgets when none exist"""
        response = await client.get("/api/v1/budgets/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["budgets"] == []

    @pytest.mark.asyncio
    async def test_list_budgets(
        self, client: AsyncClient, auth_headers: dict, test_budget: Budget
    ):
        """Test listing budgets"""
        response = await client.get("/api/v1/budgets/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["budgets"]) == 1
        assert data["budgets"][0]["name"] == "Monthly Groceries Budget"
        assert data["budgets"][0]["amount"] == "500.00"

    @pytest.mark.asyncio
    async def test_list_budgets_with_filters(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_budget: Budget,
        test_category: Category,
    ):
        """Test listing budgets with filters"""
        # Filter by period
        response = await client.get(
            "/api/v1/budgets/?period=monthly", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["total"] == 1

        # Filter by category_id
        response = await client.get(
            f"/api/v1/budgets/?category_id={test_category.id}", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["total"] == 1

        # Filter by is_active
        response = await client.get(
            "/api/v1/budgets/?is_active=true", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["total"] == 1

    @pytest.mark.asyncio
    async def test_list_budgets_pagination(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_category: Category,
        db_session: AsyncSession,
        test_user: User,
    ):
        """Test budget list pagination"""
        # Create multiple budgets
        for i in range(5):
            budget = Budget(
                user_id=test_user.id,
                category_id=test_category.id,
                name=f"Budget {i}",
                amount=Decimal("100.00"),
                currency="USD",
                period="monthly",
                start_date=date.today(),
                is_active=True,
            )
            db_session.add(budget)
        await db_session.commit()

        # Test pagination
        response = await client.get(
            "/api/v1/budgets/?skip=0&limit=2", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["budgets"]) == 2


class TestGetBudget:
    """Tests for getting a budget by ID"""

    @pytest.mark.asyncio
    async def test_get_budget(
        self, client: AsyncClient, auth_headers: dict, test_budget: Budget
    ):
        """Test getting a budget by ID"""
        response = await client.get(
            f"/api/v1/budgets/{test_budget.id}", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_budget.id
        assert data["name"] == "Monthly Groceries Budget"
        assert data["amount"] == "500.00"
        assert "total_spent" in data
        assert "remaining" in data
        assert "percentage_used" in data

    @pytest.mark.asyncio
    async def test_get_budget_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting a non-existent budget"""
        response = await client.get("/api/v1/budgets/99999", headers=auth_headers)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_budget_unauthorized(self, client: AsyncClient):
        """Test getting a budget without authentication"""
        response = await client.get("/api/v1/budgets/1")
        # FastAPI HTTPBearer returns 403 when no credentials provided
        assert response.status_code == 403


class TestCreateBudget:
    """Tests for creating budgets"""

    @pytest.mark.asyncio
    async def test_create_budget_with_category(
        self, client: AsyncClient, auth_headers: dict, test_category: Category
    ):
        """Test creating a budget with a category"""
        budget_data = {
            "name": "New Budget",
            "amount": "300.00",
            "currency": "USD",
            "period": "monthly",
            "start_date": str(date.today()),
            "category_id": test_category.id,
        }
        response = await client.post(
            "/api/v1/budgets/", headers=auth_headers, json=budget_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Budget"
        assert data["amount"] == "300.00"
        assert data["category_id"] == test_category.id

    @pytest.mark.asyncio
    async def test_create_budget_with_account(
        self, client: AsyncClient, auth_headers: dict, test_account: Account
    ):
        """Test creating a budget with an account"""
        budget_data = {
            "name": "Account Budget",
            "amount": "1000.00",
            "currency": "USD",
            "period": "monthly",
            "start_date": str(date.today()),
            "account_id": test_account.id,
        }
        response = await client.post(
            "/api/v1/budgets/", headers=auth_headers, json=budget_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Account Budget"
        assert data["account_id"] == test_account.id

    @pytest.mark.asyncio
    async def test_create_budget_without_category_or_account(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating a budget without category or account"""
        budget_data = {
            "name": "Invalid Budget",
            "amount": "300.00",
            "currency": "USD",
            "period": "monthly",
            "start_date": str(date.today()),
        }
        response = await client.post(
            "/api/v1/budgets/", headers=auth_headers, json=budget_data
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_budget_with_invalid_amount(
        self, client: AsyncClient, auth_headers: dict, test_category: Category
    ):
        """Test creating a budget with invalid amount"""
        budget_data = {
            "name": "Invalid Budget",
            "amount": "-100.00",
            "currency": "USD",
            "period": "monthly",
            "start_date": str(date.today()),
            "category_id": test_category.id,
        }
        response = await client.post(
            "/api/v1/budgets/", headers=auth_headers, json=budget_data
        )
        # Should return error (either 422 from Pydantic validation or 500 from DB constraint)
        assert response.status_code >= 400

    @pytest.mark.asyncio
    async def test_create_budget_with_custom_period(
        self, client: AsyncClient, auth_headers: dict, test_category: Category
    ):
        """Test creating a budget with custom period"""
        start_date = date.today()
        end_date = start_date + timedelta(days=30)
        budget_data = {
            "name": "Custom Budget",
            "amount": "500.00",
            "currency": "USD",
            "period": "custom",
            "start_date": str(start_date),
            "end_date": str(end_date),
            "category_id": test_category.id,
        }
        response = await client.post(
            "/api/v1/budgets/", headers=auth_headers, json=budget_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["period"] == "custom"
        assert data["end_date"] == str(end_date)

    @pytest.mark.asyncio
    async def test_create_budget_with_invalid_category(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating a budget with non-existent category"""
        budget_data = {
            "name": "Invalid Budget",
            "amount": "300.00",
            "currency": "USD",
            "period": "monthly",
            "start_date": str(date.today()),
            "category_id": 99999,
        }
        response = await client.post(
            "/api/v1/budgets/", headers=auth_headers, json=budget_data
        )
        assert response.status_code == 400


class TestUpdateBudget:
    """Tests for updating budgets"""

    @pytest.mark.asyncio
    async def test_update_budget_name(
        self, client: AsyncClient, auth_headers: dict, test_budget: Budget
    ):
        """Test updating budget name"""
        update_data = {"name": "Updated Budget Name"}
        response = await client.put(
            f"/api/v1/budgets/{test_budget.id}", headers=auth_headers, json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Budget Name"

    @pytest.mark.asyncio
    async def test_update_budget_amount(
        self, client: AsyncClient, auth_headers: dict, test_budget: Budget
    ):
        """Test updating budget amount"""
        update_data = {"amount": "600.00"}
        response = await client.put(
            f"/api/v1/budgets/{test_budget.id}", headers=auth_headers, json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == "600.00"

    @pytest.mark.asyncio
    async def test_update_budget_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating non-existent budget"""
        update_data = {"name": "Updated Name"}
        response = await client.put(
            "/api/v1/budgets/99999", headers=auth_headers, json=update_data
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_budget_is_active(
        self, client: AsyncClient, auth_headers: dict, test_budget: Budget
    ):
        """Test deactivating a budget"""
        update_data = {"is_active": False}
        response = await client.put(
            f"/api/v1/budgets/{test_budget.id}", headers=auth_headers, json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False


class TestDeleteBudget:
    """Tests for deleting budgets"""

    @pytest.mark.asyncio
    async def test_delete_budget(
        self, client: AsyncClient, auth_headers: dict, test_budget: Budget
    ):
        """Test deleting a budget"""
        response = await client.delete(
            f"/api/v1/budgets/{test_budget.id}", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "Successfully deleted" in data["message"]

        # Verify budget is deleted (soft delete)
        get_response = await client.get(
            f"/api/v1/budgets/{test_budget.id}", headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_budget_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test deleting non-existent budget"""
        response = await client.delete("/api/v1/budgets/99999", headers=auth_headers)
        assert response.status_code == 404


class TestBudgetProgress:
    """Tests for budget progress endpoint"""

    @pytest.mark.asyncio
    async def test_get_budget_progress(
        self, client: AsyncClient, auth_headers: dict, test_budget: Budget
    ):
        """Test getting budget progress"""
        response = await client.get(
            f"/api/v1/budgets/{test_budget.id}/progress", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["budget_id"] == test_budget.id
        assert data["budget_name"] == test_budget.name
        assert "total_spent" in data
        assert "remaining" in data
        assert "percentage_used" in data
        assert "is_over_budget" in data
        assert "should_alert" in data

    @pytest.mark.asyncio
    async def test_get_budget_progress_with_transactions(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_budget: Budget,
        test_account: Account,
        test_category: Category,
        db_session: AsyncSession,
        test_user: User,
    ):
        """Test budget progress with actual transactions"""
        # Create some transactions
        transaction1 = Transaction(
            user_id=test_user.id,
            account_id=test_account.id,
            category_id=test_category.id,
            amount=Decimal("100.00"),
            currency="USD",
            date=date.today(),
            description="Grocery shopping",
            type="expense",
        )
        transaction2 = Transaction(
            user_id=test_user.id,
            account_id=test_account.id,
            category_id=test_category.id,
            amount=Decimal("50.00"),
            currency="USD",
            date=date.today(),
            description="More groceries",
            type="expense",
        )
        db_session.add(transaction1)
        db_session.add(transaction2)
        await db_session.commit()

        response = await client.get(
            f"/api/v1/budgets/{test_budget.id}/progress", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["total_spent"]) == 150.00
        assert float(data["remaining"]) == 350.00
        assert float(data["percentage_used"]) == 30.00
        assert data["transaction_count"] == 2
        assert data["is_over_budget"] is False

    @pytest.mark.asyncio
    async def test_get_budget_progress_over_budget(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_budget: Budget,
        test_account: Account,
        test_category: Category,
        db_session: AsyncSession,
        test_user: User,
    ):
        """Test budget progress when over budget"""
        # Create transaction that exceeds budget
        transaction = Transaction(
            user_id=test_user.id,
            account_id=test_account.id,
            category_id=test_category.id,
            amount=Decimal("600.00"),
            currency="USD",
            date=date.today(),
            description="Over budget",
            type="expense",
        )
        db_session.add(transaction)
        await db_session.commit()

        response = await client.get(
            f"/api/v1/budgets/{test_budget.id}/progress", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["total_spent"]) == 600.00
        assert data["is_over_budget"] is True
        assert data["should_alert"] is True

    @pytest.mark.asyncio
    async def test_get_budget_progress_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting progress for non-existent budget"""
        response = await client.get(
            "/api/v1/budgets/99999/progress", headers=auth_headers
        )
        assert response.status_code == 404
