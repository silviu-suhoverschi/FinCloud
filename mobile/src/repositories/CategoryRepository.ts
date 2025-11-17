import { Q } from '@nozbe/watermelondb';
import { BaseRepository } from './BaseRepository';
import Category from '../models/Category';
import { TransactionType } from '../types';

export class CategoryRepository extends BaseRepository<Category> {
  constructor() {
    super('categories');
  }

  /**
   * Get categories by type
   */
  async getByType(userId: string, type: TransactionType): Promise<Category[]> {
    return await this.getCollection()
      .query(
        Q.where('user_id', userId),
        Q.where('type', type)
      )
      .fetch();
  }

  /**
   * Get default categories
   */
  async getDefaults(userId: string): Promise<Category[]> {
    return await this.getCollection()
      .query(
        Q.where('user_id', userId),
        Q.where('is_default', true)
      )
      .fetch();
  }

  /**
   * Get parent categories (top-level)
   */
  async getParentCategories(userId: string): Promise<Category[]> {
    return await this.getCollection()
      .query(
        Q.where('user_id', userId),
        Q.where('parent_id', null)
      )
      .fetch();
  }

  /**
   * Get subcategories
   */
  async getSubcategories(parentId: string): Promise<Category[]> {
    return await this.getCollection()
      .query(Q.where('parent_id', parentId))
      .fetch();
  }

  /**
   * Search categories by name
   */
  async searchByName(userId: string, name: string): Promise<Category[]> {
    return await this.getCollection()
      .query(
        Q.where('user_id', userId),
        Q.where('name', Q.like(`%${Q.sanitizeLikeString(name)}%`))
      )
      .fetch();
  }
}

export default new CategoryRepository();
