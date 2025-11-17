import { Model } from '@nozbe/watermelondb';
import { field, date, readonly } from '@nozbe/watermelondb/decorators';

export default class Account extends Model {
  static table = 'accounts';

  @field('user_id') userId!: string;
  @field('name') name!: string;
  @field('type') type!: string;
  @field('currency') currency!: string;
  @field('balance') balance!: number;
  @field('initial_balance') initialBalance!: number;
  @field('description') description?: string;
  @field('is_active') isActive!: boolean;
  @readonly @date('created_at') createdAt!: Date;
  @date('updated_at') updatedAt!: Date;
  @date('synced_at') syncedAt?: Date;
}
