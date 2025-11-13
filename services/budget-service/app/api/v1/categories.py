"""
Categories API endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.category import Category
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryWithChildren,
    CategoryList,
    CategoryTree,
    CategoryType,
)
from app.services.category_service import CategoryService

router = APIRouter()


@router.get("/", response_model=CategoryList)
async def list_categories(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Max number of records to return"
    ),
    type: Optional[CategoryType] = Query(None, description="Filter by category type"),
    parent_id: Optional[int] = Query(
        None,
        description="Filter by parent category ID (use 'null' for root categories)",
    ),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by category name"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all categories for the current user with optional filters.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **type**: Filter by category type (income, expense, transfer)
    - **parent_id**: Filter by parent category ID
    - **is_active**: Filter by active status
    - **search**: Search by category name (partial match)
    """
    # Build query filters
    filters = [Category.user_id == current_user.id, Category.deleted_at.is_(None)]

    if type is not None:
        filters.append(Category.type == type.value)

    if parent_id is not None:
        filters.append(Category.parent_id == parent_id)

    if is_active is not None:
        filters.append(Category.is_active == is_active)

    if search is not None:
        filters.append(Category.name.ilike(f"%{search}%"))

    # Get total count
    count_query = select(func.count()).select_from(Category).filter(and_(*filters))
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Get categories with pagination
    query = (
        select(Category)
        .filter(and_(*filters))
        .order_by(Category.sort_order, Category.name)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    categories = result.scalars().all()

    return CategoryList(total=total, categories=categories)


@router.get("/tree", response_model=CategoryTree)
async def get_category_tree(
    type: Optional[CategoryType] = Query(None, description="Filter by category type"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get hierarchical category tree for the current user.

    Returns categories organized in a parent-child tree structure.

    - **type**: Filter by category type (income, expense, transfer)
    """
    root_categories = await CategoryService.build_category_tree(
        db, current_user.id, type.value if type else None
    )

    return CategoryTree(categories=root_categories)


@router.get("/{category_id}", response_model=CategoryWithChildren)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific category by ID with its children.

    - **category_id**: Category ID
    """
    category = await CategoryService.get_category_with_children(
        db, category_id, current_user.id
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )

    return category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new category for the current user.

    - **name**: Category name (required)
    - **type**: Category type - income, expense, or transfer (required)
    - **parent_id**: Parent category ID for hierarchical categories (optional)
    - **color**: Category color in hex format (optional, e.g., #FF5733)
    - **icon**: Icon identifier (optional)
    - **is_active**: Whether the category is active (optional, default: true)
    - **sort_order**: Sort order for displaying categories (optional, default: 0)
    """
    # Validate category data
    try:
        await CategoryService.validate_category_data(
            db,
            current_user.id,
            category_data.name,
            category_data.parent_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Create new category
    new_category = Category(
        user_id=current_user.id,
        name=category_data.name,
        type=category_data.type.value,
        parent_id=category_data.parent_id,
        color=category_data.color,
        icon=category_data.icon,
        is_active=category_data.is_active,
        sort_order=category_data.sort_order,
    )

    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)

    return new_category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing category.

    - **category_id**: Category ID
    - **name**: Category name (optional)
    - **type**: Category type (optional)
    - **parent_id**: Parent category ID (optional)
    - **color**: Category color (optional)
    - **icon**: Icon identifier (optional)
    - **is_active**: Active status (optional)
    - **sort_order**: Sort order (optional)
    """
    # Get existing category
    query = select(Category).filter(
        and_(
            Category.id == category_id,
            Category.user_id == current_user.id,
            Category.deleted_at.is_(None),
        )
    )
    result = await db.execute(query)
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )

    # Validate if name or parent_id is being changed
    if category_data.name is not None or category_data.parent_id is not None:
        try:
            await CategoryService.validate_category_data(
                db,
                current_user.id,
                category_data.name if category_data.name is not None else category.name,
                (
                    category_data.parent_id
                    if category_data.parent_id is not None
                    else category.parent_id
                ),
                category_id=category_id,
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Update fields
    if category_data.name is not None:
        category.name = category_data.name
    if category_data.type is not None:
        category.type = category_data.type.value
    if category_data.parent_id is not None:
        category.parent_id = category_data.parent_id
    if category_data.color is not None:
        category.color = category_data.color
    if category_data.icon is not None:
        category.icon = category_data.icon
    if category_data.is_active is not None:
        category.is_active = category_data.is_active
    if category_data.sort_order is not None:
        category.sort_order = category_data.sort_order

    category.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(category)

    return category


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(
    category_id: int,
    force: bool = Query(False, description="Force delete even if category is in use"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a category (soft delete).

    This will also delete all child categories in the hierarchy.

    - **category_id**: Category ID
    - **force**: Force delete even if category is used in transactions or budgets (default: false)
    """
    # Get existing category
    query = select(Category).filter(
        and_(
            Category.id == category_id,
            Category.user_id == current_user.id,
            Category.deleted_at.is_(None),
        )
    )
    result = await db.execute(query)
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )

    # Check if category is in use
    if not force:
        usage = await CategoryService.check_category_usage(db, category_id)
        if usage["is_used"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Category is in use by {usage['transaction_count']} transaction(s) "
                    f"and {usage['budget_count']} budget(s). "
                    f"Use force=true to delete anyway or deactivate the category instead."
                ),
            )

    # Soft delete the category and its children
    deleted_count = await CategoryService.soft_delete_category_tree(db, category)

    await db.commit()

    return {
        "message": f"Successfully deleted category and {deleted_count - 1} child categories",
        "deleted_count": deleted_count,
    }


@router.get("/{category_id}/usage", response_model=dict)
async def get_category_usage(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get usage statistics for a category.

    Returns how many transactions and budgets use this category.

    - **category_id**: Category ID
    """
    # Verify category exists and belongs to user
    query = select(Category).filter(
        and_(
            Category.id == category_id,
            Category.user_id == current_user.id,
            Category.deleted_at.is_(None),
        )
    )
    result = await db.execute(query)
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )

    usage = await CategoryService.check_category_usage(db, category_id)

    return {"category_id": category_id, "category_name": category.name, **usage}
