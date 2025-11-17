import { Model } from '@nozbe/watermelondb';
import { field, date, readonly } from '@nozbe/watermelondb/decorators';

export default class Category extends Model {
  static table = 'categories';

  @field('user_id') userId!: string;
  @field('name') name!: string;
  @field('type') type!: string;
  @field('icon') icon?: string;
  @field('color') color?: string;
  @field('parent_id') parentId?: string;
  @field('is_default') isDefault!: boolean;
  @readonly @date('created_at') createdAt!: Date;
  @date('updated_at') updatedAt!: Date;
  @date('synced_at') syncedAt?: Date;
}
