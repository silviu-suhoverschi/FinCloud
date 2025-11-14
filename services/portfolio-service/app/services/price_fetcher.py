"""
Base price fetcher interface and common utilities
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


@dataclass
class PriceData:
    """Price data container"""

    symbol: str
    date: date
    close: Decimal
    open: Optional[Decimal] = None
    high: Optional[Decimal] = None
    low: Optional[Decimal] = None
    adjusted_close: Optional[Decimal] = None
    volume: Optional[int] = None
    source: str = "unknown"


class BasePriceFetcher(ABC):
    """Base class for price fetching services"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    async def fetch_current_price(
        self, symbol: str, asset_type: str
    ) -> Optional[PriceData]:
        """
        Fetch current price for a symbol

        Args:
            symbol: Asset symbol
            asset_type: Type of asset (stock, etf, crypto, etc.)

        Returns:
            PriceData object or None if not found
        """
        pass

    @abstractmethod
    async def fetch_historical_prices(
        self,
        symbol: str,
        asset_type: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[PriceData]:
        """
        Fetch historical prices for a symbol

        Args:
            symbol: Asset symbol
            asset_type: Type of asset
            start_date: Start date for historical data
            end_date: End date for historical data

        Returns:
            List of PriceData objects
        """
        pass

    @abstractmethod
    def supports_asset_type(self, asset_type: str) -> bool:
        """
        Check if this fetcher supports the given asset type

        Args:
            asset_type: Type of asset to check

        Returns:
            True if supported, False otherwise
        """
        pass

    def _convert_to_decimal(self, value: any) -> Optional[Decimal]:
        """Convert value to Decimal, handling None and errors"""
        if value is None or value == "":
            return None
        try:
            return Decimal(str(value))
        except (ValueError, TypeError) as e:
            self.logger.warning(f"Failed to convert {value} to Decimal: {e}")
            return None

    def _convert_to_int(self, value: any) -> Optional[int]:
        """Convert value to int, handling None and errors"""
        if value is None or value == "":
            return None
        try:
            return int(value)
        except (ValueError, TypeError) as e:
            self.logger.warning(f"Failed to convert {value} to int: {e}")
            return None
