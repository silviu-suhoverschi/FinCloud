import { Model } from '@nozbe/watermelondb';
import { field, date, readonly, json } from '@nozbe/watermelondb/decorators';

export default class Transaction extends Model {
  static table = 'transactions';

  @field('user_id') userId!: string;
  @field('account_id') accountId!: string;
  @field('type') type!: string;
  @field('amount') amount!: number;
  @field('currency') currency!: string;
  @field('description') description!: string;
  @date('date') date!: Date;
  @field('category_id') categoryId?: string;
  @json('tags', (json) => json) tags!: string[];
  @field('recurring') recurring!: boolean;
  @field('recurring_id') recurringId?: string;
  @json('attachments', (json) => json) attachments!: string[];
  @field('destination_account_id') destinationAccountId?: string;
  @readonly @date('created_at') createdAt!: Date;
  @date('updated_at') updatedAt!: Date;
  @date('synced_at') syncedAt?: Date;
}
