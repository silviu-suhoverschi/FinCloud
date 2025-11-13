"""
Category service layer for business logic.

Handles category creation, updates, and hierarchy management.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy import inspect as sqlalchemy_inspect
from datetime import datetime

from app.models.category import Category
from app.models.transaction import Transaction
from app.models.budget import Budget


class CategoryService:
    """Service for managing categories and hierarchies."""

    @staticmethod
    async def validate_category_data(
        db: AsyncSession,
        user_id: int,
        name: str,
        parent_id: Optional[int] = None,
        category_id: Optional[int] = None,
    ) -> None:
        """
        Validate category data.

        Args:
            db: Database session
            user_id: User ID
            name: Category name
            parent_id: Parent category ID (for hierarchy)
            category_id: Current category ID (for updates, to exclude self)

        Raises:
            ValueError: If validation fails
        """
        # Check for duplicate name under the same parent
        filters = [
            Category.user_id == user_id,
            Category.name == name,
            Category.deleted_at.is_(None),
        ]

        # Add parent_id filter
        if parent_id is not None:
            filters.append(Category.parent_id == parent_id)
        else:
            filters.append(Category.parent_id.is_(None))

        # Exclude current category when updating
        if category_id is not None:
            filters.append(Category.id != category_id)

        query = select(Category).filter(and_(*filters))
        result = await db.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            parent_msg = f" under parent category {parent_id}" if parent_id else ""
            raise ValueError(
                f"Category with name '{name}'{parent_msg} already exists"
            )

        # Validate parent category exists and belongs to user
        if parent_id is not None:
            parent_query = select(Category).filter(
                and_(
                    Category.id == parent_id,
                    Category.user_id == user_id,
                    Category.deleted_at.is_(None),
                )
            )
            result = await db.execute(parent_query)
            parent = result.scalar_one_or_none()

            if not parent:
                raise ValueError(
                    f"Parent category with ID {parent_id} not found or does not belong to user"
                )

            # Prevent circular references during update
            if category_id is not None and category_id == parent_id:
                raise ValueError("Category cannot be its own parent")

            # Check for circular reference in hierarchy
            if category_id is not None:
                if await CategoryService.would_create_circular_reference(
                    db, category_id, parent_id
                ):
                    raise ValueError(
                        "Cannot set parent: would create circular reference in category hierarchy"
                    )

    @staticmethod
    async def would_create_circular_reference(
        db: AsyncSession,
        category_id: int,
        new_parent_id: int,
    ) -> bool:
        """
        Check if setting new_parent_id as parent would create a circular reference.

        Args:
            db: Database session
            category_id: Category ID being updated
            new_parent_id: New parent ID to check

        Returns:
            True if circular reference would be created, False otherwise
        """
        # Walk up the parent chain from new_parent_id
        current_parent_id = new_parent_id

        while current_parent_id is not None:
            # If we encounter our own category_id in the parent chain, it's circular
            if current_parent_id == category_id:
                return True

            # Get the next parent
            query = select(Category.parent_id).filter(
                and_(
                    Category.id == current_parent_id,
                    Category.deleted_at.is_(None),
                )
            )
            result = await db.execute(query)
            current_parent_id = result.scalar_one_or_none()

        return False

    @staticmethod
    async def get_category_with_children(
        db: AsyncSession,
        category_id: int,
        user_id: int,
    ) -> Optional[Category]:
        """
        Get category with all its children loaded.

        Args:
            db: Database session
            category_id: Category ID
            user_id: User ID

        Returns:
            Category with children or None
        """
        query = select(Category).filter(
            and_(
                Category.id == category_id,
                Category.user_id == user_id,
                Category.deleted_at.is_(None),
            )
        )
        result = await db.execute(query)
        category = result.scalar_one_or_none()

        if category:
            # Load children
            await db.refresh(category, ["children"])

        return category

    @staticmethod
    async def build_category_tree(
        db: AsyncSession,
        user_id: int,
        category_type: Optional[str] = None,
    ) -> List[Category]:
        """
        Build a hierarchical tree of categories.

        Args:
            db: Database session
            user_id: User ID
            category_type: Filter by category type (optional)

        Returns:
            List of root categories with children loaded
        """
        # Get all categories for the user
        filters = [
            Category.user_id == user_id,
            Category.deleted_at.is_(None),
        ]

        if category_type:
            filters.append(Category.type == category_type)

        query = (
            select(Category)
            .filter(and_(*filters))
            .order_by(Category.sort_order, Category.name)
        )
        result = await db.execute(query)
        all_categories = result.scalars().all()

        # Build a map of categories by ID
        category_map = {cat.id: cat for cat in all_categories}

        # Build parent-child relationships
        root_categories = []
        for category in all_categories:
            if category.parent_id is None:
                root_categories.append(category)
            elif category.parent_id in category_map:
                parent = category_map[category.parent_id]
                # Initialize children list if not exists
                if not hasattr(parent, '_children_list'):
                    parent._children_list = []
                parent._children_list.append(category)

        # Set children attribute for all categories using SQLAlchemy's state API to bypass lazy loading
        for category in all_categories:
            # Get the SQLAlchemy instance state
            state = sqlalchemy_inspect(category)
            # Directly set the attribute in the instance dict, bypassing the descriptor
            if hasattr(category, '_children_list'):
                state.dict['children'] = category._children_list
            else:
                state.dict['children'] = []

        return root_categories

    @staticmethod
    async def check_category_usage(
        db: AsyncSession,
        category_id: int,
    ) -> dict:
        """
        Check how many times a category is used in transactions and budgets.

        Args:
            db: Database session
            category_id: Category ID

        Returns:
            Dictionary with usage counts
        """
        # Count transactions
        transaction_query = select(func.count()).select_from(Transaction).filter(
            and_(
                Transaction.category_id == category_id,
                Transaction.deleted_at.is_(None),
            )
        )
        transaction_result = await db.execute(transaction_query)
        transaction_count = transaction_result.scalar()

        # Count budgets
        budget_query = select(func.count()).select_from(Budget).filter(
            and_(
                Budget.category_id == category_id,
                Budget.deleted_at.is_(None),
            )
        )
        budget_result = await db.execute(budget_query)
        budget_count = budget_result.scalar()

        return {
            "transaction_count": transaction_count,
            "budget_count": budget_count,
            "is_used": transaction_count > 0 or budget_count > 0,
        }

    @staticmethod
    async def soft_delete_category_tree(
        db: AsyncSession,
        category: Category,
    ) -> int:
        """
        Soft delete a category and all its children recursively.

        Args:
            db: Database session
            category: Category to delete

        Returns:
            Number of categories deleted
        """
        count = 0
        now = datetime.utcnow()

        # Load children if not loaded
        await db.refresh(category, ["children"])

        # Recursively delete children first
        for child in category.children:
            count += await CategoryService.soft_delete_category_tree(db, child)

        # Soft delete the category
        category.deleted_at = now
        count += 1

        return count
