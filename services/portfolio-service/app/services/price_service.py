"""
Price service with caching, rate limiting, and retry logic
"""

import json
import asyncio
from datetime import date
from typing import Optional, List
from decimal import Decimal
import redis.asyncio as aioredis
import logging

from app.core.config import settings
from app.services.price_fetcher import BasePriceFetcher, PriceData
from app.services.yahoo_finance_fetcher import YahooFinanceFetcher
from app.services.alpha_vantage_fetcher import AlphaVantageFetcher
from app.services.coingecko_fetcher import CoinGeckoFetcher

logger = logging.getLogger(__name__)


class PriceService:
    """
    Price service that orchestrates multiple price fetchers with caching and rate limiting
    """

    CACHE_TTL_SECONDS = 3600  # 1 hour cache for prices
    RATE_LIMIT_WINDOW = 60  # 1 minute window for rate limiting
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 2

    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None
        self.fetchers: List[BasePriceFetcher] = []
        self._initialize_fetchers()

    def _initialize_fetchers(self):
        """Initialize all available price fetchers"""
        # Yahoo Finance (no API key needed)
        if settings.YAHOO_FINANCE_ENABLED:
            self.fetchers.append(YahooFinanceFetcher())
            logger.info("Initialized Yahoo Finance fetcher")

        # Alpha Vantage (requires API key)
        if settings.ALPHA_VANTAGE_API_KEY and settings.ALPHA_VANTAGE_API_KEY != "demo":
            self.fetchers.append(AlphaVantageFetcher(settings.ALPHA_VANTAGE_API_KEY))
            logger.info("Initialized Alpha Vantage fetcher")

        # CoinGecko (optional API key for higher limits)
        coingecko_key = (
            settings.COINGECKO_API_KEY if settings.COINGECKO_API_KEY else None
        )
        self.fetchers.append(CoinGeckoFetcher(coingecko_key))
        logger.info("Initialized CoinGecko fetcher")

        if not self.fetchers:
            logger.warning("No price fetchers initialized!")

    async def _get_redis_client(self) -> aioredis.Redis:
        """Get or create Redis client"""
        if not self.redis_client:
            self.redis_client = await aioredis.from_url(
                settings.REDIS_URL, encoding="utf-8", decode_responses=True
            )
        return self.redis_client

    def _get_cache_key(self, symbol: str, price_type: str = "current") -> str:
        """Generate cache key for price data"""
        return f"price:{price_type}:{symbol.upper()}"

    def _get_rate_limit_key(self, fetcher_name: str) -> str:
        """Generate rate limit key for a fetcher"""
        return f"ratelimit:{fetcher_name}"

    async def _check_rate_limit(self, fetcher_name: str) -> bool:
        """Check if rate limit allows another request"""
        try:
            redis = await self._get_redis_client()
            key = self._get_rate_limit_key(fetcher_name)

            # Get current count
            count = await redis.get(key)
            if count is None:
                # First request in window
                await redis.setex(key, self.RATE_LIMIT_WINDOW, "1")
                return True

            # Rate limits per provider
            limits = {
                "yahoo_finance": 2000,  # Very high, no official limit
                "alpha_vantage": 5,  # Free tier: 5 per minute, 500 per day
                "coingecko": 10,  # Free tier: 10-50 per minute depending on endpoint
            }

            limit = limits.get(fetcher_name, 10)
            if int(count) < limit:
                await redis.incr(key)
                return True

            logger.warning(f"Rate limit reached for {fetcher_name}")
            return False

        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True  # Allow on error

    async def _get_cached_price(self, symbol: str) -> Optional[PriceData]:
        """Get cached price data"""
        try:
            redis = await self._get_redis_client()
            key = self._get_cache_key(symbol)
            cached = await redis.get(key)

            if cached:
                data = json.loads(cached)
                logger.debug(f"Cache hit for {symbol}")
                return PriceData(
                    symbol=data["symbol"],
                    date=date.fromisoformat(data["date"]),
                    close=Decimal(data["close"]),
                    open=Decimal(data["open"]) if data.get("open") else None,
                    high=Decimal(data["high"]) if data.get("high") else None,
                    low=Decimal(data["low"]) if data.get("low") else None,
                    adjusted_close=(
                        Decimal(data["adjusted_close"])
                        if data.get("adjusted_close")
                        else None
                    ),
                    volume=data.get("volume"),
                    source=data["source"],
                )
            return None

        except Exception as e:
            logger.error(f"Error getting cached price: {e}")
            return None

    async def _cache_price(self, price_data: PriceData):
        """Cache price data"""
        try:
            redis = await self._get_redis_client()
            key = self._get_cache_key(price_data.symbol)

            data = {
                "symbol": price_data.symbol,
                "date": price_data.date.isoformat(),
                "close": str(price_data.close),
                "open": str(price_data.open) if price_data.open else None,
                "high": str(price_data.high) if price_data.high else None,
                "low": str(price_data.low) if price_data.low else None,
                "adjusted_close": (
                    str(price_data.adjusted_close)
                    if price_data.adjusted_close
                    else None
                ),
                "volume": price_data.volume,
                "source": price_data.source,
            }

            await redis.setex(key, self.CACHE_TTL_SECONDS, json.dumps(data))
            logger.debug(f"Cached price for {price_data.symbol}")

        except Exception as e:
            logger.error(f"Error caching price: {e}")

    async def fetch_price_with_retry(
        self, symbol: str, asset_type: str, use_cache: bool = True
    ) -> Optional[PriceData]:
        """
        Fetch price with caching, rate limiting, and retry logic

        Args:
            symbol: Asset symbol
            asset_type: Type of asset
            use_cache: Whether to use cached data

        Returns:
            PriceData or None
        """
        # Check cache first
        if use_cache:
            cached_price = await self._get_cached_price(symbol)
            if cached_price:
                return cached_price

        # Try each fetcher in order
        for fetcher in self.fetchers:
            if not fetcher.supports_asset_type(asset_type):
                continue

            # Check rate limit
            if not await self._check_rate_limit(fetcher.SOURCE_NAME):
                logger.warning(f"Skipping {fetcher.SOURCE_NAME} due to rate limit")
                continue

            # Retry loop
            for attempt in range(self.MAX_RETRIES):
                try:
                    price_data = await fetcher.fetch_current_price(symbol, asset_type)

                    if price_data:
                        # Cache the result
                        await self._cache_price(price_data)
                        return price_data

                except Exception as e:
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.MAX_RETRIES} failed for {symbol} "
                        f"using {fetcher.SOURCE_NAME}: {e}"
                    )

                    if attempt < self.MAX_RETRIES - 1:
                        await asyncio.sleep(self.RETRY_DELAY_SECONDS * (attempt + 1))

        logger.error(f"Failed to fetch price for {symbol} after trying all fetchers")
        return None

    async def fetch_historical_prices(
        self,
        symbol: str,
        asset_type: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[PriceData]:
        """
        Fetch historical prices with retry logic

        Args:
            symbol: Asset symbol
            asset_type: Type of asset
            start_date: Start date
            end_date: End date

        Returns:
            List of PriceData
        """
        # Try each fetcher in order
        for fetcher in self.fetchers:
            if not fetcher.supports_asset_type(asset_type):
                continue

            # Check rate limit
            if not await self._check_rate_limit(fetcher.SOURCE_NAME):
                logger.warning(f"Skipping {fetcher.SOURCE_NAME} due to rate limit")
                continue

            # Retry loop
            for attempt in range(self.MAX_RETRIES):
                try:
                    prices = await fetcher.fetch_historical_prices(
                        symbol, asset_type, start_date, end_date
                    )

                    if prices:
                        return prices

                except Exception as e:
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.MAX_RETRIES} failed for {symbol} "
                        f"historical data using {fetcher.SOURCE_NAME}: {e}"
                    )

                    if attempt < self.MAX_RETRIES - 1:
                        await asyncio.sleep(self.RETRY_DELAY_SECONDS * (attempt + 1))

        logger.error(
            f"Failed to fetch historical prices for {symbol} after trying all fetchers"
        )
        return []

    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
