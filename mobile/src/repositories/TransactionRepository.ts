import { Q } from '@nozbe/watermelondb';
import { BaseRepository } from './BaseRepository';
import Transaction from '../models/Transaction';
import { TransactionType } from '../types';

export class TransactionRepository extends BaseRepository<Transaction> {
  constructor() {
    super('transactions');
  }

  /**
   * Get transactions by account
   */
  async getByAccount(accountId: string): Promise<Transaction[]> {
    return await this.getCollection()
      .query(Q.where('account_id', accountId))
      .fetch();
  }

  /**
   * Get transactions by type
   */
  async getByType(userId: string, type: TransactionType): Promise<Transaction[]> {
    return await this.getCollection()
      .query(
        Q.where('user_id', userId),
        Q.where('type', type)
      )
      .fetch();
  }

  /**
   * Get transactions by category
   */
  async getByCategory(categoryId: string): Promise<Transaction[]> {
    return await this.getCollection()
      .query(Q.where('category_id', categoryId))
      .fetch();
  }

  /**
   * Get transactions by date range
   */
  async getByDateRange(userId: string, startDate: Date, endDate: Date): Promise<Transaction[]> {
    return await this.getCollection()
      .query(
        Q.where('user_id', userId),
        Q.where('date', Q.between(startDate.getTime(), endDate.getTime())),
        Q.sortBy('date', Q.desc)
      )
      .fetch();
  }

  /**
   * Get recent transactions
   */
  async getRecent(userId: string, limit: number = 10): Promise<Transaction[]> {
    return await this.getCollection()
      .query(
        Q.where('user_id', userId),
        Q.sortBy('date', Q.desc),
        Q.take(limit)
      )
      .fetch();
  }

  /**
   * Get recurring transactions
   */
  async getRecurring(userId: string): Promise<Transaction[]> {
    return await this.getCollection()
      .query(
        Q.where('user_id', userId),
        Q.where('recurring', true)
      )
      .fetch();
  }

  /**
   * Search transactions
   */
  async search(userId: string, searchTerm: string): Promise<Transaction[]> {
    return await this.getCollection()
      .query(
        Q.where('user_id', userId),
        Q.where('description', Q.like(`%${Q.sanitizeLikeString(searchTerm)}%`))
      )
      .fetch();
  }

  /**
   * Get total by type and date range
   */
  async getTotalByType(
    userId: string,
    type: TransactionType,
    startDate: Date,
    endDate: Date
  ): Promise<number> {
    const transactions = await this.getCollection()
      .query(
        Q.where('user_id', userId),
        Q.where('type', type),
        Q.where('date', Q.between(startDate.getTime(), endDate.getTime()))
      )
      .fetch();

    return transactions.reduce((sum, transaction) => sum + transaction.amount, 0);
  }

  /**
   * Get expenses by category for date range
   */
  async getExpensesByCategory(
    userId: string,
    startDate: Date,
    endDate: Date
  ): Promise<Map<string, number>> {
    const transactions = await this.getCollection()
      .query(
        Q.where('user_id', userId),
        Q.where('type', TransactionType.EXPENSE),
        Q.where('date', Q.between(startDate.getTime(), endDate.getTime()))
      )
      .fetch();

    const categoryTotals = new Map<string, number>();
    transactions.forEach((transaction) => {
      const categoryId = transaction.categoryId || 'uncategorized';
      const current = categoryTotals.get(categoryId) || 0;
      categoryTotals.set(categoryId, current + transaction.amount);
    });

    return categoryTotals;
  }
}

export default new TransactionRepository();
