import { portfolioAssetRepository } from '../repositories';

/**
 * Yahoo Finance API Service
 * Free tier has limitations, consider using alternative APIs in production
 */

export interface PriceQuote {
  symbol: string;
  price: number;
  currency: string;
  change: number;
  changePercent: number;
  timestamp: Date;
}

class PriceUpdateService {
  private readonly YAHOO_FINANCE_API = 'https://query1.finance.yahoo.com/v8/finance/chart';

  /**
   * Fetch current price for a single symbol from Yahoo Finance
   */
  async fetchPrice(symbol: string): Promise<PriceQuote | null> {
    try {
      const url = `${this.YAHOO_FINANCE_API}/${symbol}?interval=1d&range=1d`;
      const response = await fetch(url);

      if (!response.ok) {
        console.error(`Failed to fetch price for ${symbol}:`, response.status);
        return null;
      }

      const data = await response.json();
      const result = data.chart?.result?.[0];

      if (!result) {
        console.error(`No data found for ${symbol}`);
        return null;
      }

      const meta = result.meta;
      const price = meta.regularMarketPrice;
      const previousClose = meta.previousClose;
      const change = price - previousClose;
      const changePercent = (change / previousClose) * 100;

      return {
        symbol: meta.symbol,
        price,
        currency: meta.currency,
        change,
        changePercent,
        timestamp: new Date(),
      };
    } catch (error) {
      console.error(`Error fetching price for ${symbol}:`, error);
      return null;
    }
  }

  /**
   * Fetch prices for multiple symbols
   */
  async fetchPrices(symbols: string[]): Promise<Map<string, PriceQuote>> {
    const prices = new Map<string, PriceQuote>();

    // Fetch prices in parallel with a limit to avoid rate limiting
    const BATCH_SIZE = 5;
    for (let i = 0; i < symbols.length; i += BATCH_SIZE) {
      const batch = symbols.slice(i, i + BATCH_SIZE);
      const results = await Promise.allSettled(
        batch.map((symbol) => this.fetchPrice(symbol))
      );

      results.forEach((result, index) => {
        if (result.status === 'fulfilled' && result.value) {
          prices.set(batch[index], result.value);
        }
      });

      // Small delay to avoid rate limiting
      if (i + BATCH_SIZE < symbols.length) {
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
    }

    return prices;
  }

  /**
   * Update prices for all portfolio assets for a user
   */
  async updateAllAssetPrices(userId: string): Promise<{
    updated: number;
    failed: number;
  }> {
    let updated = 0;
    let failed = 0;

    try {
      const assets = await portfolioAssetRepository.getByUserId(userId);

      if (assets.length === 0) {
        return { updated, failed };
      }

      // Extract unique symbols
      const symbols = [...new Set(assets.map((asset) => asset.symbol))];

      // Fetch all prices
      const prices = await this.fetchPrices(symbols);

      // Update each asset
      for (const asset of assets) {
        const quote = prices.get(asset.symbol);

        if (quote) {
          try {
            await portfolioAssetRepository.updatePrice(
              asset.id,
              quote.price,
              new Date()
            );
            updated++;
          } catch (error) {
            console.error(`Error updating asset ${asset.id}:`, error);
            failed++;
          }
        } else {
          failed++;
        }
      }
    } catch (error) {
      console.error('Error updating asset prices:', error);
    }

    return { updated, failed };
  }

  /**
   * Update price for a single asset
   */
  async updateAssetPrice(assetId: string, symbol: string): Promise<boolean> {
    try {
      const quote = await this.fetchPrice(symbol);

      if (!quote) {
        return false;
      }

      await portfolioAssetRepository.updatePrice(
        assetId,
        quote.price,
        new Date()
      );

      return true;
    } catch (error) {
      console.error(`Error updating asset ${assetId}:`, error);
      return false;
    }
  }

  /**
   * Search for stock symbols (basic implementation)
   * In production, use a dedicated search API
   */
  async searchSymbol(query: string): Promise<Array<{
    symbol: string;
    name: string;
    type: string;
    exchange: string;
  }>> {
    try {
      const url = `https://query2.finance.yahoo.com/v1/finance/search?q=${encodeURIComponent(query)}`;
      const response = await fetch(url);

      if (!response.ok) {
        return [];
      }

      const data = await response.json();
      const quotes = data.quotes || [];

      return quotes
        .filter((quote: any) =>
          quote.quoteType === 'EQUITY' ||
          quote.quoteType === 'ETF' ||
          quote.quoteType === 'CRYPTOCURRENCY'
        )
        .slice(0, 10)
        .map((quote: any) => ({
          symbol: quote.symbol,
          name: quote.shortname || quote.longname,
          type: quote.quoteType,
          exchange: quote.exchange,
        }));
    } catch (error) {
      console.error('Error searching symbol:', error);
      return [];
    }
  }

  /**
   * Get crypto price from CoinGecko (alternative for crypto)
   */
  async fetchCryptoPrice(cryptoId: string): Promise<PriceQuote | null> {
    try {
      const url = `https://api.coingecko.com/api/v3/simple/price?ids=${cryptoId}&vs_currencies=usd&include_24hr_change=true`;
      const response = await fetch(url);

      if (!response.ok) {
        return null;
      }

      const data = await response.json();
      const priceData = data[cryptoId];

      if (!priceData) {
        return null;
      }

      return {
        symbol: cryptoId.toUpperCase(),
        price: priceData.usd,
        currency: 'USD',
        change: 0,
        changePercent: priceData.usd_24h_change || 0,
        timestamp: new Date(),
      };
    } catch (error) {
      console.error(`Error fetching crypto price for ${cryptoId}:`, error);
      return null;
    }
  }
}

export const priceUpdateService = new PriceUpdateService();
