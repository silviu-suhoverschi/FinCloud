"""
Pydantic schemas for the portfolio service.
"""

from app.schemas.portfolio import (
    PortfolioBase,
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioResponse,
    PortfolioList,
)
from app.schemas.holding import (
    HoldingBase,
    HoldingCreate,
    HoldingUpdate,
    HoldingResponse,
    HoldingWithAssetResponse,
    HoldingList,
)
from app.schemas.transaction import (
    TransactionType,
    TransactionBase,
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionWithAssetResponse,
    TransactionList,
)

__all__ = [
    # Portfolio schemas
    "PortfolioBase",
    "PortfolioCreate",
    "PortfolioUpdate",
    "PortfolioResponse",
    "PortfolioList",
    # Holding schemas
    "HoldingBase",
    "HoldingCreate",
    "HoldingUpdate",
    "HoldingResponse",
    "HoldingWithAssetResponse",
    "HoldingList",
    # Transaction schemas
    "TransactionType",
    "TransactionBase",
    "TransactionCreate",
    "TransactionUpdate",
    "TransactionResponse",
    "TransactionWithAssetResponse",
    "TransactionList",
]
