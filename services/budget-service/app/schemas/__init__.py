"""
Pydantic schemas for the budget service.
"""

from app.schemas.auth import (
    UserRegister,
    UserLogin,
    Token,
    TokenRefresh,
    AccessToken,
    UserResponse,
    UserUpdate,
    PasswordChange,
    PasswordResetRequest,
    PasswordReset,
    RoleEnum,
    UserWithRole,
    EmailVerificationRequest,
)

from app.schemas.account import (
    AccountType,
    AccountBase,
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    AccountBalance,
    AccountList,
)

from app.schemas.transaction import (
    TransactionType,
    TransactionBase,
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionList,
    TransactionBulkCreate,
    TransactionBulkResponse,
    TransactionSearchParams,
)

from app.schemas.category import (
    CategoryType,
    CategoryBase,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryWithChildren,
    CategoryList,
    CategoryTree,
)

__all__ = [
    # Auth schemas
    "UserRegister",
    "UserLogin",
    "Token",
    "TokenRefresh",
    "AccessToken",
    "UserResponse",
    "UserUpdate",
    "PasswordChange",
    "PasswordResetRequest",
    "PasswordReset",
    "RoleEnum",
    "UserWithRole",
    "EmailVerificationRequest",
    # Account schemas
    "AccountType",
    "AccountBase",
    "AccountCreate",
    "AccountUpdate",
    "AccountResponse",
    "AccountBalance",
    "AccountList",
    # Transaction schemas
    "TransactionType",
    "TransactionBase",
    "TransactionCreate",
    "TransactionUpdate",
    "TransactionResponse",
    "TransactionList",
    "TransactionBulkCreate",
    "TransactionBulkResponse",
    "TransactionSearchParams",
    # Category schemas
    "CategoryType",
    "CategoryBase",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "CategoryWithChildren",
    "CategoryList",
    "CategoryTree",
]
