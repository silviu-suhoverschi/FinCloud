import { Model } from '@nozbe/watermelondb';
import { field, date, readonly } from '@nozbe/watermelondb/decorators';

export default class PortfolioTransaction extends Model {
  static table = 'portfolio_transactions';

  @field('user_id') userId!: string;
  @field('asset_id') assetId!: string;
  @field('type') type!: string;
  @field('quantity') quantity!: number;
  @field('price') price!: number;
  @field('fees') fees!: number;
  @field('total') total!: number;
  @field('currency') currency!: string;
  @date('date') date!: Date;
  @field('notes') notes?: string;
  @readonly @date('created_at') createdAt!: Date;
  @date('updated_at') updatedAt!: Date;
  @date('synced_at') syncedAt?: Date;
}
