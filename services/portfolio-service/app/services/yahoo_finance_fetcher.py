"""
Yahoo Finance price fetcher implementation
"""

import yfinance as yf
from datetime import date, timedelta
from typing import Optional, List
import asyncio
from functools import partial

from app.services.price_fetcher import BasePriceFetcher, PriceData


class YahooFinanceFetcher(BasePriceFetcher):
    """Yahoo Finance price fetcher"""

    SOURCE_NAME = "yahoo_finance"

    def __init__(self):
        super().__init__(api_key=None)  # Yahoo Finance doesn't require API key

    def supports_asset_type(self, asset_type: str) -> bool:
        """Yahoo Finance supports stocks, ETFs, mutual funds, commodities, and some crypto"""
        supported_types = ["stock", "etf", "mutual_fund", "commodity", "index"]
        return asset_type.lower() in supported_types

    async def fetch_current_price(
        self, symbol: str, asset_type: str
    ) -> Optional[PriceData]:
        """Fetch current price from Yahoo Finance"""
        if not self.supports_asset_type(asset_type):
            self.logger.debug(f"Asset type {asset_type} not supported by Yahoo Finance")
            return None

        try:
            # Run yfinance in executor to avoid blocking
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, partial(yf.Ticker, symbol))

            # Get current price info
            info = await loop.run_in_executor(None, lambda: ticker.info)

            # Try to get the current price from various fields
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")

            if not current_price:
                self.logger.warning(f"No current price found for {symbol}")
                return None

            # Get the most recent trading day
            today = date.today()

            price_data = PriceData(
                symbol=symbol,
                date=today,
                close=self._convert_to_decimal(current_price),
                open=self._convert_to_decimal(info.get("regularMarketOpen")),
                high=self._convert_to_decimal(info.get("regularMarketDayHigh")),
                low=self._convert_to_decimal(info.get("regularMarketDayLow")),
                volume=self._convert_to_int(info.get("regularMarketVolume")),
                source=self.SOURCE_NAME,
            )

            self.logger.info(f"Fetched current price for {symbol}: {price_data.close}")
            return price_data

        except Exception as e:
            self.logger.error(f"Error fetching current price for {symbol}: {e}")
            return None

    async def fetch_historical_prices(
        self,
        symbol: str,
        asset_type: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[PriceData]:
        """Fetch historical prices from Yahoo Finance"""
        if not self.supports_asset_type(asset_type):
            self.logger.debug(f"Asset type {asset_type} not supported by Yahoo Finance")
            return []

        try:
            # Default to last 30 days if no dates provided
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)

            # Run yfinance in executor
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, partial(yf.Ticker, symbol))

            # Download historical data
            history = await loop.run_in_executor(
                None,
                partial(
                    ticker.history,
                    start=start_date.isoformat(),
                    end=(end_date + timedelta(days=1)).isoformat(),
                ),
            )

            if history.empty:
                self.logger.warning(f"No historical data found for {symbol}")
                return []

            # Convert DataFrame to PriceData objects
            price_data_list = []
            for idx, row in history.iterrows():
                price_data = PriceData(
                    symbol=symbol,
                    date=idx.date(),
                    open=self._convert_to_decimal(row.get("Open")),
                    high=self._convert_to_decimal(row.get("High")),
                    low=self._convert_to_decimal(row.get("Low")),
                    close=self._convert_to_decimal(row.get("Close")),
                    adjusted_close=self._convert_to_decimal(row.get("Close")),
                    volume=self._convert_to_int(row.get("Volume")),
                    source=self.SOURCE_NAME,
                )
                if price_data.close:
                    price_data_list.append(price_data)

            self.logger.info(
                f"Fetched {len(price_data_list)} historical prices for {symbol}"
            )
            return price_data_list

        except Exception as e:
            self.logger.error(f"Error fetching historical prices for {symbol}: {e}")
            return []
