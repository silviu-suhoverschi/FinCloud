import { Model } from '@nozbe/watermelondb';
import { field, date, readonly } from '@nozbe/watermelondb/decorators';

export default class Budget extends Model {
  static table = 'budgets';

  @field('user_id') userId!: string;
  @field('category_id') categoryId!: string;
  @field('amount') amount!: number;
  @field('currency') currency!: string;
  @field('period') period!: string;
  @date('start_date') startDate!: Date;
  @date('end_date') endDate?: Date;
  @field('spent') spent!: number;
  @readonly @date('created_at') createdAt!: Date;
  @date('updated_at') updatedAt!: Date;
  @date('synced_at') syncedAt?: Date;
}
