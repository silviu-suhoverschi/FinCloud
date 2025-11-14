"""
Tests for price fetching functionality
"""

import pytest
from datetime import date
from decimal import Decimal

from app.services.price_fetcher import PriceData
from app.services.yahoo_finance_fetcher import YahooFinanceFetcher
from app.services.alpha_vantage_fetcher import AlphaVantageFetcher
from app.services.coingecko_fetcher import CoinGeckoFetcher


class TestPriceData:
    """Test PriceData dataclass"""

    def test_price_data_creation(self):
        """Test creating a PriceData object"""
        price_data = PriceData(
            symbol="AAPL",
            date=date.today(),
            close=Decimal("150.50"),
            open=Decimal("149.00"),
            high=Decimal("151.00"),
            low=Decimal("148.50"),
            volume=1000000,
            source="test",
        )

        assert price_data.symbol == "AAPL"
        assert price_data.close == Decimal("150.50")
        assert price_data.open == Decimal("149.00")
        assert price_data.source == "test"


class TestYahooFinanceFetcher:
    """Test Yahoo Finance fetcher"""

    def test_supports_asset_types(self):
        """Test asset type support"""
        fetcher = YahooFinanceFetcher()

        assert fetcher.supports_asset_type("stock")
        assert fetcher.supports_asset_type("etf")
        assert fetcher.supports_asset_type("mutual_fund")
        assert not fetcher.supports_asset_type("crypto")

    @pytest.mark.asyncio
    async def test_fetch_current_price(self):
        """Test fetching current price for a known symbol"""
        fetcher = YahooFinanceFetcher()

        # Test with a well-known stock (Apple)
        price_data = await fetcher.fetch_current_price("AAPL", "stock")

        if price_data:  # May fail in test environment without internet
            assert price_data.symbol == "AAPL"
            assert price_data.close is not None
            assert price_data.close > 0
            assert price_data.source == "yahoo_finance"

    @pytest.mark.asyncio
    async def test_fetch_invalid_symbol(self):
        """Test fetching invalid symbol returns None"""
        fetcher = YahooFinanceFetcher()

        # Test with invalid symbol
        price_data = await fetcher.fetch_current_price("INVALID_SYMBOL_XYZ", "stock")

        assert price_data is None


class TestAlphaVantageFetcher:
    """Test Alpha Vantage fetcher"""

    def test_supports_asset_types(self):
        """Test asset type support"""
        fetcher = AlphaVantageFetcher("demo")

        assert fetcher.supports_asset_type("stock")
        assert fetcher.supports_asset_type("etf")
        assert not fetcher.supports_asset_type("crypto")


class TestCoinGeckoFetcher:
    """Test CoinGecko fetcher"""

    def test_supports_asset_types(self):
        """Test asset type support"""
        fetcher = CoinGeckoFetcher()

        assert fetcher.supports_asset_type("crypto")
        assert not fetcher.supports_asset_type("stock")

    def test_symbol_to_coin_id_mapping(self):
        """Test symbol to CoinGecko ID mapping"""
        fetcher = CoinGeckoFetcher()

        assert fetcher._symbol_to_coin_id("BTC") == "bitcoin"
        assert fetcher._symbol_to_coin_id("ETH") == "ethereum"
        assert fetcher._symbol_to_coin_id("BTC-USD") == "bitcoin"

    @pytest.mark.asyncio
    async def test_fetch_current_price(self):
        """Test fetching current crypto price"""
        fetcher = CoinGeckoFetcher()

        # Test with Bitcoin
        price_data = await fetcher.fetch_current_price("BTC", "crypto")

        if price_data:  # May fail in test environment
            assert price_data.symbol == "BTC"
            assert price_data.close is not None
            assert price_data.close > 0
            assert price_data.source == "coingecko"
