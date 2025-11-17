import { Q } from '@nozbe/watermelondb';
import { BaseRepository } from './BaseRepository';
import PortfolioAsset from '../models/PortfolioAsset';
import PortfolioTransaction from '../models/PortfolioTransaction';
import { AssetType } from '../types';

export class PortfolioAssetRepository extends BaseRepository<PortfolioAsset> {
  constructor() {
    super('portfolio_assets');
  }

  /**
   * Get assets by type
   */
  async getByType(userId: string, type: AssetType): Promise<PortfolioAsset[]> {
    return await this.getCollection()
      .query(
        Q.where('user_id', userId),
        Q.where('type', type)
      )
      .fetch();
  }

  /**
   * Get asset by symbol
   */
  async getBySymbol(userId: string, symbol: string): Promise<PortfolioAsset | null> {
    const assets = await this.getCollection()
      .query(
        Q.where('user_id', userId),
        Q.where('symbol', symbol)
      )
      .fetch();

    return assets[0] || null;
  }

  /**
   * Get total portfolio value
   */
  async getTotalValue(userId: string): Promise<number> {
    const assets = await this.getByUserId(userId);
    return assets.reduce((sum, asset) => sum + asset.marketValue, 0);
  }

  /**
   * Get total gain/loss
   */
  async getTotalGainLoss(userId: string): Promise<number> {
    const assets = await this.getByUserId(userId);
    return assets.reduce((sum, asset) => sum + asset.gainLoss, 0);
  }

  /**
   * Get assets needing price update
   */
  async getNeedingPriceUpdate(userId: string, hours: number = 1): Promise<PortfolioAsset[]> {
    const cutoffTime = Date.now() - hours * 60 * 60 * 1000;
    const assets = await this.getByUserId(userId);

    return assets.filter((asset) => {
      if (!asset.lastPriceUpdate) return true;
      return asset.lastPriceUpdate.getTime() < cutoffTime;
    });
  }

  /**
   * Update asset price
   */
  async updatePrice(id: string, price: number): Promise<PortfolioAsset> {
    const asset = await this.getById(id);
    if (!asset) {
      throw new Error('Asset not found');
    }

    const marketValue = asset.quantity * price;
    const gainLoss = marketValue - asset.totalCost;
    const gainLossPercentage = asset.totalCost > 0 ? (gainLoss / asset.totalCost) * 100 : 0;

    return await this.update(id, {
      currentPrice: price,
      marketValue,
      gainLoss,
      gainLossPercentage,
      lastPriceUpdate: new Date(),
    } as any);
  }
}

export class PortfolioTransactionRepository extends BaseRepository<PortfolioTransaction> {
  constructor() {
    super('portfolio_transactions');
  }

  /**
   * Get transactions by asset
   */
  async getByAsset(assetId: string): Promise<PortfolioTransaction[]> {
    return await this.getCollection()
      .query(
        Q.where('asset_id', assetId),
        Q.sortBy('date', Q.desc)
      )
      .fetch();
  }

  /**
   * Get transactions by type
   */
  async getByType(userId: string, type: 'buy' | 'sell' | 'dividend'): Promise<PortfolioTransaction[]> {
    return await this.getCollection()
      .query(
        Q.where('user_id', userId),
        Q.where('type', type)
      )
      .fetch();
  }

  /**
   * Get transactions by date range
   */
  async getByDateRange(userId: string, startDate: Date, endDate: Date): Promise<PortfolioTransaction[]> {
    return await this.getCollection()
      .query(
        Q.where('user_id', userId),
        Q.where('date', Q.between(startDate.getTime(), endDate.getTime())),
        Q.sortBy('date', Q.desc)
      )
      .fetch();
  }

  /**
   * Get total invested amount
   */
  async getTotalInvested(userId: string): Promise<number> {
    const buyTransactions = await this.getByType(userId, 'buy');
    return buyTransactions.reduce((sum, transaction) => sum + transaction.total, 0);
  }
}

export const portfolioAssetRepository = new PortfolioAssetRepository();
export const portfolioTransactionRepository = new PortfolioTransactionRepository();
