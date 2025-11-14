"""
Alpha Vantage price fetcher implementation
"""

from alpha_vantage.timeseries import TimeSeries
from datetime import date, datetime, timedelta
from typing import Optional, List
import asyncio
from functools import partial

from app.services.price_fetcher import BasePriceFetcher, PriceData


class AlphaVantageFetcher(BasePriceFetcher):
    """Alpha Vantage price fetcher"""

    SOURCE_NAME = "alpha_vantage"

    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)
        if not api_key or api_key == "demo":
            self.logger.warning(
                "Using demo API key for Alpha Vantage - limited to 5 requests per minute"
            )

    def supports_asset_type(self, asset_type: str) -> bool:
        """Alpha Vantage supports stocks, ETFs"""
        supported_types = ["stock", "etf"]
        return asset_type.lower() in supported_types

    async def fetch_current_price(
        self, symbol: str, asset_type: str
    ) -> Optional[PriceData]:
        """Fetch current price from Alpha Vantage"""
        if not self.supports_asset_type(asset_type):
            self.logger.debug(f"Asset type {asset_type} not supported by Alpha Vantage")
            return None

        try:
            loop = asyncio.get_event_loop()

            # Initialize TimeSeries
            ts = await loop.run_in_executor(
                None, partial(TimeSeries, key=self.api_key, output_format="json")
            )

            # Get intraday data (last refreshed)
            data, meta_data = await loop.run_in_executor(
                None, partial(ts.get_quote_endpoint, symbol=symbol)
            )

            if not data:
                self.logger.warning(f"No data returned for {symbol}")
                return None

            # Parse the quote data
            price_str = data.get("05. price")
            if not price_str:
                self.logger.warning(f"No price field in data for {symbol}")
                return None

            # Get the latest trading day
            latest_trading_day = data.get("07. latest trading day")
            if latest_trading_day:
                price_date = datetime.strptime(latest_trading_day, "%Y-%m-%d").date()
            else:
                price_date = date.today()

            price_data = PriceData(
                symbol=symbol,
                date=price_date,
                close=self._convert_to_decimal(price_str),
                open=self._convert_to_decimal(data.get("02. open")),
                high=self._convert_to_decimal(data.get("03. high")),
                low=self._convert_to_decimal(data.get("04. low")),
                volume=self._convert_to_int(data.get("06. volume")),
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
        """Fetch historical prices from Alpha Vantage"""
        if not self.supports_asset_type(asset_type):
            self.logger.debug(f"Asset type {asset_type} not supported by Alpha Vantage")
            return []

        try:
            loop = asyncio.get_event_loop()

            # Initialize TimeSeries
            ts = await loop.run_in_executor(
                None, partial(TimeSeries, key=self.api_key, output_format="json")
            )

            # Get daily data (full output for historical)
            data, meta_data = await loop.run_in_executor(
                None, partial(ts.get_daily, symbol=symbol, outputsize="full")
            )

            if not data:
                self.logger.warning(f"No historical data returned for {symbol}")
                return []

            # Default date range if not provided
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)

            # Convert data to PriceData objects
            price_data_list = []
            for date_str, values in data.items():
                price_date = datetime.strptime(date_str, "%Y-%m-%d").date()

                # Filter by date range
                if price_date < start_date or price_date > end_date:
                    continue

                price_data = PriceData(
                    symbol=symbol,
                    date=price_date,
                    open=self._convert_to_decimal(values.get("1. open")),
                    high=self._convert_to_decimal(values.get("2. high")),
                    low=self._convert_to_decimal(values.get("3. low")),
                    close=self._convert_to_decimal(values.get("4. close")),
                    adjusted_close=self._convert_to_decimal(
                        values.get("5. adjusted close")
                    ),
                    volume=self._convert_to_int(values.get("6. volume")),
                    source=self.SOURCE_NAME,
                )

                if price_data.close:
                    price_data_list.append(price_data)

            # Sort by date
            price_data_list.sort(key=lambda x: x.date)

            self.logger.info(
                f"Fetched {len(price_data_list)} historical prices for {symbol}"
            )
            return price_data_list

        except Exception as e:
            self.logger.error(f"Error fetching historical prices for {symbol}: {e}")
            return []
