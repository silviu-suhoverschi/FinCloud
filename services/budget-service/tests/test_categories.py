"""
Tests for category endpoints
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from decimal import Decimal

from app.models.user import User
from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime, timedelta


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
async def test_parent_category(db_session: AsyncSession, test_user: User) -> Category:
    """Create a test parent category"""
    category = Category(
        user_id=test_user.id,
        name="Food & Dining",
        type="expense",
        color="#00FF00",
        is_active=True,
        sort_order=0,
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest_asyncio.fixture(scope="function")
async def test_child_category(
    db_session: AsyncSession, test_user: User, test_parent_category: Category
) -> Category:
    """Create a test child category"""
    category = Category(
        user_id=test_user.id,
        name="Restaurant",
        type="expense",
        parent_id=test_parent_category.id,
        is_active=True,
        sort_order=1,
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


class TestListCategories:
    """Tests for listing categories"""

    @pytest.mark.asyncio
    async def test_list_categories_empty(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test listing categories when none exist"""
        response = await client.get("/api/v1/categories/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["categories"] == []

    @pytest.mark.asyncio
    async def test_list_categories(
        self, client: AsyncClient, auth_headers: dict, test_category: Category
    ):
        """Test listing categories"""
        response = await client.get("/api/v1/categories/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["categories"]) == 1
        assert data["categories"][0]["name"] == "Groceries"
        assert data["categories"][0]["type"] == "expense"

    @pytest.mark.asyncio
    async def test_list_categories_with_filters(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_category: Category,
        test_parent_category: Category,
    ):
        """Test listing categories with filters"""
        # Filter by type
        response = await client.get(
            "/api/v1/categories/?type=expense", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["total"] == 2

        # Filter by name search
        response = await client.get(
            "/api/v1/categories/?search=Food", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["total"] == 1
        assert response.json()["categories"][0]["name"] == "Food & Dining"

    @pytest.mark.asyncio
    async def test_list_categories_unauthorized(self, client: AsyncClient):
        """Test listing categories without authentication"""
        response = await client.get("/api/v1/categories/")
        assert response.status_code == 401


class TestGetCategory:
    """Tests for getting a single category"""

    @pytest.mark.asyncio
    async def test_get_category(
        self, client: AsyncClient, auth_headers: dict, test_category: Category
    ):
        """Test getting a category by ID"""
        response = await client.get(
            f"/api/v1/categories/{test_category.id}", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_category.id
        assert data["name"] == "Groceries"
        assert data["type"] == "expense"
        assert data["color"] == "#FF5733"

    @pytest.mark.asyncio
    async def test_get_category_with_children(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_parent_category: Category,
        test_child_category: Category,
    ):
        """Test getting a category with children"""
        response = await client.get(
            f"/api/v1/categories/{test_parent_category.id}", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_parent_category.id
        assert "children" in data
        assert len(data["children"]) == 1
        assert data["children"][0]["name"] == "Restaurant"

    @pytest.mark.asyncio
    async def test_get_category_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting a non-existent category"""
        response = await client.get("/api/v1/categories/99999", headers=auth_headers)
        assert response.status_code == 404


class TestCreateCategory:
    """Tests for creating categories"""

    @pytest.mark.asyncio
    async def test_create_category(self, client: AsyncClient, auth_headers: dict):
        """Test creating a new category"""
        category_data = {
            "name": "Transportation",
            "type": "expense",
            "color": "#0000FF",
            "icon": "car",
            "is_active": True,
            "sort_order": 0,
        }
        response = await client.post(
            "/api/v1/categories/", json=category_data, headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Transportation"
        assert data["type"] == "expense"
        assert data["color"] == "#0000FF"
        assert data["icon"] == "car"

    @pytest.mark.asyncio
    async def test_create_category_minimal(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating a category with minimal data"""
        category_data = {
            "name": "Utilities",
            "type": "expense",
        }
        response = await client.post(
            "/api/v1/categories/", json=category_data, headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Utilities"
        assert data["type"] == "expense"
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_create_category_with_parent(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_parent_category: Category,
    ):
        """Test creating a child category"""
        category_data = {
            "name": "Fast Food",
            "type": "expense",
            "parent_id": test_parent_category.id,
        }
        response = await client.post(
            "/api/v1/categories/", json=category_data, headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Fast Food"
        assert data["parent_id"] == test_parent_category.id

    @pytest.mark.asyncio
    async def test_create_category_duplicate_name(
        self, client: AsyncClient, auth_headers: dict, test_category: Category
    ):
        """Test creating a category with duplicate name"""
        category_data = {
            "name": "Groceries",
            "type": "expense",
        }
        response = await client.post(
            "/api/v1/categories/", json=category_data, headers=auth_headers
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_category_invalid_parent(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating a category with non-existent parent"""
        category_data = {
            "name": "Test Category",
            "type": "expense",
            "parent_id": 99999,
        }
        response = await client.post(
            "/api/v1/categories/", json=category_data, headers=auth_headers
        )
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]


class TestUpdateCategory:
    """Tests for updating categories"""

    @pytest.mark.asyncio
    async def test_update_category(
        self, client: AsyncClient, auth_headers: dict, test_category: Category
    ):
        """Test updating a category"""
        update_data = {
            "name": "Supermarket",
            "color": "#00FF00",
        }
        response = await client.put(
            f"/api/v1/categories/{test_category.id}",
            json=update_data,
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Supermarket"
        assert data["color"] == "#00FF00"

    @pytest.mark.asyncio
    async def test_update_category_parent(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_category: Category,
        test_parent_category: Category,
    ):
        """Test updating a category's parent"""
        update_data = {"parent_id": test_parent_category.id}
        response = await client.put(
            f"/api/v1/categories/{test_category.id}",
            json=update_data,
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["parent_id"] == test_parent_category.id

    @pytest.mark.asyncio
    async def test_update_category_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating a non-existent category"""
        update_data = {"name": "Updated Name"}
        response = await client.put(
            "/api/v1/categories/99999", json=update_data, headers=auth_headers
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_category_circular_reference(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_parent_category: Category,
        test_child_category: Category,
    ):
        """Test preventing circular reference in hierarchy"""
        # Try to make parent category a child of its own child
        update_data = {"parent_id": test_child_category.id}
        response = await client.put(
            f"/api/v1/categories/{test_parent_category.id}",
            json=update_data,
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "circular" in response.json()["detail"].lower()


class TestDeleteCategory:
    """Tests for deleting categories"""

    @pytest.mark.asyncio
    async def test_delete_category(
        self, client: AsyncClient, auth_headers: dict, test_category: Category
    ):
        """Test deleting a category"""
        response = await client.delete(
            f"/api/v1/categories/{test_category.id}", headers=auth_headers
        )
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()

        # Verify category is deleted
        response = await client.get(
            f"/api/v1/categories/{test_category.id}", headers=auth_headers
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_category_with_children(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_parent_category: Category,
        test_child_category: Category,
    ):
        """Test deleting a category with children"""
        response = await client.delete(
            f"/api/v1/categories/{test_parent_category.id}", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["deleted_count"] == 2  # Parent + child

    @pytest.mark.asyncio
    async def test_delete_category_in_use(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        test_category: Category,
        db_session: AsyncSession,
    ):
        """Test deleting a category that is in use"""
        # Create an account
        account = Account(
            user_id=test_user.id,
            name="Test Account",
            type="checking",
            currency="USD",
            initial_balance=Decimal("1000.00"),
            current_balance=Decimal("1000.00"),
        )
        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        # Create a transaction using this category
        transaction = Transaction(
            user_id=test_user.id,
            account_id=account.id,
            category_id=test_category.id,
            type="expense",
            amount=Decimal("50.00"),
            currency="USD",
            date=date.today(),
            description="Test transaction",
        )
        db_session.add(transaction)
        await db_session.commit()

        # Try to delete the category without force
        response = await client.delete(
            f"/api/v1/categories/{test_category.id}", headers=auth_headers
        )
        assert response.status_code == 400
        assert "in use" in response.json()["detail"]

        # Delete with force=true
        response = await client.delete(
            f"/api/v1/categories/{test_category.id}?force=true", headers=auth_headers
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_category_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test deleting a non-existent category"""
        response = await client.delete("/api/v1/categories/99999", headers=auth_headers)
        assert response.status_code == 404


class TestCategoryTree:
    """Tests for category tree endpoint"""

    @pytest.mark.asyncio
    async def test_get_category_tree(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_parent_category: Category,
        test_child_category: Category,
    ):
        """Test getting the category tree"""
        response = await client.get("/api/v1/categories/tree", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) == 1  # One root category
        assert data["categories"][0]["name"] == "Food & Dining"
        assert len(data["categories"][0]["children"]) == 1
        assert data["categories"][0]["children"][0]["name"] == "Restaurant"

    @pytest.mark.asyncio
    async def test_get_category_tree_filtered(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_parent_category: Category,
        db_session: AsyncSession,
        test_user: User,
    ):
        """Test getting the category tree filtered by type"""
        # Create an income category
        income_category = Category(
            user_id=test_user.id,
            name="Salary",
            type="income",
        )
        db_session.add(income_category)
        await db_session.commit()

        # Get only expense categories
        response = await client.get(
            "/api/v1/categories/tree?type=expense", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["categories"]) == 1
        assert data["categories"][0]["type"] == "expense"


class TestCategoryUsage:
    """Tests for category usage endpoint"""

    @pytest.mark.asyncio
    async def test_get_category_usage(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        test_category: Category,
        db_session: AsyncSession,
    ):
        """Test getting category usage statistics"""
        # Create account and transaction
        account = Account(
            user_id=test_user.id,
            name="Test Account",
            type="checking",
            currency="USD",
            initial_balance=Decimal("1000.00"),
            current_balance=Decimal("950.00"),
        )
        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        transaction = Transaction(
            user_id=test_user.id,
            account_id=account.id,
            category_id=test_category.id,
            type="expense",
            amount=Decimal("50.00"),
            currency="USD",
            date=date.today(),
            description="Test transaction",
        )
        db_session.add(transaction)
        await db_session.commit()

        # Get usage
        response = await client.get(
            f"/api/v1/categories/{test_category.id}/usage", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["category_id"] == test_category.id
        assert data["transaction_count"] == 1
        assert data["budget_count"] == 0
        assert data["is_used"] is True

    @pytest.mark.asyncio
    async def test_get_category_usage_unused(
        self, client: AsyncClient, auth_headers: dict, test_category: Category
    ):
        """Test getting usage for an unused category"""
        response = await client.get(
            f"/api/v1/categories/{test_category.id}/usage", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_count"] == 0
        assert data["budget_count"] == 0
        assert data["is_used"] is False
