"""
CoinGecko price fetcher implementation for cryptocurrency
"""

from pycoingecko import CoinGeckoAPI
from datetime import date, datetime, timedelta
from typing import Optional, List
import asyncio
from functools import partial

from app.services.price_fetcher import BasePriceFetcher, PriceData


class CoinGeckoFetcher(BasePriceFetcher):
    """CoinGecko price fetcher for cryptocurrency"""

    SOURCE_NAME = "coingecko"

    # Common crypto symbol to CoinGecko ID mapping
    SYMBOL_TO_ID = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "USDT": "tether",
        "BNB": "binancecoin",
        "USDC": "usd-coin",
        "XRP": "ripple",
        "ADA": "cardano",
        "DOGE": "dogecoin",
        "SOL": "solana",
        "DOT": "polkadot",
        "MATIC": "matic-network",
        "LTC": "litecoin",
        "AVAX": "avalanche-2",
        "LINK": "chainlink",
        "UNI": "uniswap",
        "ATOM": "cosmos",
        "XLM": "stellar",
        "BCH": "bitcoin-cash",
        "ALGO": "algorand",
        "VET": "vechain",
    }

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key=api_key)
        # CoinGecko free tier doesn't require API key
        # Pro tier can use API key for higher rate limits
        if api_key:
            self.cg = CoinGeckoAPI(api_key=api_key)
        else:
            self.cg = CoinGeckoAPI()

    def supports_asset_type(self, asset_type: str) -> bool:
        """CoinGecko supports crypto assets"""
        return asset_type.lower() == "crypto"

    def _symbol_to_coin_id(self, symbol: str) -> str:
        """Convert crypto symbol to CoinGecko coin ID"""
        # Remove common suffixes like -USD, -USDT, etc.
        clean_symbol = symbol.upper().replace("-USD", "").replace("-USDT", "")

        # Check our mapping first
        if clean_symbol in self.SYMBOL_TO_ID:
            return self.SYMBOL_TO_ID[clean_symbol]

        # Otherwise, try lowercase symbol as ID (common pattern)
        return symbol.lower()

    async def fetch_current_price(
        self, symbol: str, asset_type: str
    ) -> Optional[PriceData]:
        """Fetch current price from CoinGecko"""
        if not self.supports_asset_type(asset_type):
            self.logger.debug(f"Asset type {asset_type} not supported by CoinGecko")
            return None

        try:
            coin_id = self._symbol_to_coin_id(symbol)
            loop = asyncio.get_event_loop()

            # Get current price data
            data = await loop.run_in_executor(
                None,
                partial(
                    self.cg.get_price,
                    ids=coin_id,
                    vs_currencies="usd",
                    include_market_cap=True,
                    include_24hr_vol=True,
                    include_24hr_change=True,
                    include_last_updated_at=True,
                ),
            )

            if not data or coin_id not in data:
                self.logger.warning(
                    f"No data returned for {symbol} (coin_id: {coin_id})"
                )
                return None

            coin_data = data[coin_id]
            price = coin_data.get("usd")

            if not price:
                self.logger.warning(f"No price found for {symbol}")
                return None

            # Get timestamp or use today
            timestamp = coin_data.get("last_updated_at")
            if timestamp:
                price_date = datetime.fromtimestamp(timestamp).date()
            else:
                price_date = date.today()

            price_data = PriceData(
                symbol=symbol,
                date=price_date,
                close=self._convert_to_decimal(price),
                volume=self._convert_to_int(coin_data.get("usd_24h_vol")),
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
        """Fetch historical prices from CoinGecko"""
        if not self.supports_asset_type(asset_type):
            self.logger.debug(f"Asset type {asset_type} not supported by CoinGecko")
            return []

        try:
            coin_id = self._symbol_to_coin_id(symbol)
            loop = asyncio.get_event_loop()

            # Default date range if not provided
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)

            # Calculate number of days
            days = (end_date - start_date).days + 1

            # Get market chart data
            data = await loop.run_in_executor(
                None,
                partial(
                    self.cg.get_coin_market_chart_by_id,
                    id=coin_id,
                    vs_currency="usd",
                    days=days,
                ),
            )

            if not data or "prices" not in data:
                self.logger.warning(
                    f"No historical data returned for {symbol} (coin_id: {coin_id})"
                )
                return []

            # Convert data to PriceData objects
            price_data_list = []
            for timestamp, price in data["prices"]:
                price_date = datetime.fromtimestamp(timestamp / 1000).date()

                # Filter by date range
                if price_date < start_date or price_date > end_date:
                    continue

                # Get volume for this timestamp if available
                volume = None
                if "total_volumes" in data:
                    # Find matching volume entry
                    for vol_timestamp, vol in data["total_volumes"]:
                        vol_date = datetime.fromtimestamp(vol_timestamp / 1000).date()
                        if vol_date == price_date:
                            volume = self._convert_to_int(vol)
                            break

                price_data = PriceData(
                    symbol=symbol,
                    date=price_date,
                    close=self._convert_to_decimal(price),
                    volume=volume,
                    source=self.SOURCE_NAME,
                )

                if price_data.close:
                    price_data_list.append(price_data)

            # Remove duplicates (keep latest for each date)
            unique_prices = {}
            for pd in price_data_list:
                if pd.date not in unique_prices:
                    unique_prices[pd.date] = pd

            price_data_list = list(unique_prices.values())
            price_data_list.sort(key=lambda x: x.date)

            self.logger.info(
                f"Fetched {len(price_data_list)} historical prices for {symbol}"
            )
            return price_data_list

        except Exception as e:
            self.logger.error(f"Error fetching historical prices for {symbol}: {e}")
            return []
