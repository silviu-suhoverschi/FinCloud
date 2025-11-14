"""
Celery tasks for price updates
"""

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import logging

from app.celery_app import celery_app
from app.core.config import settings
from app.models.asset import Asset
from app.models.holding import Holding
from app.models.price_history import PriceHistory
from app.services.price_service import PriceService

logger = logging.getLogger(__name__)


async def get_db_session():
    """Create async database session"""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session:
        yield session


async def update_asset_price_async(asset_id: int, symbol: str, asset_type: str):
    """Async helper to update a single asset price"""
    price_service = PriceService()

    try:
        # Fetch current price
        price_data = await price_service.fetch_price_with_retry(symbol, asset_type)

        if not price_data:
            logger.warning(f"Could not fetch price for {symbol} ({asset_type})")
            return {"symbol": symbol, "status": "failed", "error": "No price data"}

        # Save to database
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        async_session_maker = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session_maker() as session:
            # Check if price already exists for today
            stmt = select(PriceHistory).where(
                PriceHistory.asset_id == asset_id,
                PriceHistory.date == price_data.date,
                PriceHistory.source == price_data.source,
            )
            result = await session.execute(stmt)
            existing_price = result.scalar_one_or_none()

            if existing_price:
                # Update existing price
                existing_price.open = price_data.open
                existing_price.high = price_data.high
                existing_price.low = price_data.low
                existing_price.close = price_data.close
                existing_price.adjusted_close = price_data.adjusted_close
                existing_price.volume = price_data.volume
                logger.info(f"Updated existing price for {symbol}")
            else:
                # Create new price entry
                new_price = PriceHistory(
                    asset_id=asset_id,
                    date=price_data.date,
                    open=price_data.open,
                    high=price_data.high,
                    low=price_data.low,
                    close=price_data.close,
                    adjusted_close=price_data.adjusted_close,
                    volume=price_data.volume,
                    source=price_data.source,
                )
                session.add(new_price)
                logger.info(f"Created new price entry for {symbol}")

            await session.commit()

        await engine.dispose()

        return {
            "symbol": symbol,
            "status": "success",
            "price": str(price_data.close),
            "date": price_data.date.isoformat(),
            "source": price_data.source,
        }

    except Exception as e:
        logger.error(f"Error updating price for {symbol}: {e}", exc_info=True)
        return {"symbol": symbol, "status": "error", "error": str(e)}

    finally:
        await price_service.close()


async def update_all_prices_async():
    """Async helper to update all asset prices"""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    try:
        async with async_session_maker() as session:
            # Get all active assets that are currently held in portfolios
            stmt = (
                select(Asset)
                .join(Holding)
                .where(Asset.is_active)
                .where(Holding.quantity > 0)
                .distinct()
            )
            result = await session.execute(stmt)
            assets = result.scalars().all()

            logger.info(f"Found {len(assets)} assets to update")

            if not assets:
                return {
                    "status": "completed",
                    "updated": 0,
                    "message": "No assets to update",
                }

        # Update prices for each asset
        results = []
        for asset in assets:
            result = await update_asset_price_async(asset.id, asset.symbol, asset.type)
            results.append(result)

            # Small delay between requests to avoid overwhelming APIs
            await asyncio.sleep(0.5)

        # Count successes
        successful = sum(1 for r in results if r["status"] == "success")
        failed = sum(1 for r in results if r["status"] in ["failed", "error"])

        logger.info(f"Price update completed: {successful} successful, {failed} failed")

        return {
            "status": "completed",
            "total": len(assets),
            "successful": successful,
            "failed": failed,
            "results": results,
        }

    except Exception as e:
        logger.error(f"Error in update_all_prices_async: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}

    finally:
        await engine.dispose()


@celery_app.task(bind=True, max_retries=3)
def update_all_prices(self):
    """Update prices for all tracked assets"""
    logger.info("Starting price update task")
    try:
        result = asyncio.run(update_all_prices_async())
        return result
    except Exception as e:
        logger.error(f"Error in update_all_prices task: {e}")
        raise self.retry(exc=e, countdown=300)  # Retry after 5 minutes


@celery_app.task(bind=True, max_retries=3)
def update_asset_price(self, asset_id: int, symbol: str, asset_type: str):
    """Update price for a specific asset"""
    logger.info(f"Updating price for {symbol} ({asset_type})")
    try:
        result = asyncio.run(update_asset_price_async(asset_id, symbol, asset_type))
        return result
    except Exception as e:
        logger.error(f"Error in update_asset_price task: {e}")
        raise self.retry(exc=e, countdown=60)  # Retry after 1 minute
