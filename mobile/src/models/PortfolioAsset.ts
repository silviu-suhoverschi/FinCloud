import { Model } from '@nozbe/watermelondb';
import { field, date, readonly } from '@nozbe/watermelondb/decorators';

export default class PortfolioAsset extends Model {
  static table = 'portfolio_assets';

  @field('user_id') userId!: string;
  @field('symbol') symbol!: string;
  @field('name') name!: string;
  @field('type') type!: string;
  @field('quantity') quantity!: number;
  @field('average_cost') averageCost!: number;
  @field('current_price') currentPrice!: number;
  @field('currency') currency!: string;
  @field('market_value') marketValue!: number;
  @field('total_cost') totalCost!: number;
  @field('gain_loss') gainLoss!: number;
  @field('gain_loss_percentage') gainLossPercentage!: number;
  @date('last_price_update') lastPriceUpdate?: Date;
  @readonly @date('created_at') createdAt!: Date;
  @date('updated_at') updatedAt!: Date;
  @date('synced_at') syncedAt?: Date;
}
