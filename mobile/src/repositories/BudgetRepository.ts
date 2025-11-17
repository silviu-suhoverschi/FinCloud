import { Q } from '@nozbe/watermelondb';
import { BaseRepository } from './BaseRepository';
import Budget from '../models/Budget';

export class BudgetRepository extends BaseRepository<Budget> {
  constructor() {
    super('budgets');
  }

  /**
   * Get budgets by category
   */
  async getByCategory(categoryId: string): Promise<Budget[]> {
    return await this.getCollection()
      .query(Q.where('category_id', categoryId))
      .fetch();
  }

  /**
   * Get budgets by period
   */
  async getByPeriod(userId: string, period: 'weekly' | 'monthly' | 'yearly'): Promise<Budget[]> {
    return await this.getCollection()
      .query(
        Q.where('user_id', userId),
        Q.where('period', period)
      )
      .fetch();
  }

  /**
   * Get active budgets for current date
   */
  async getActive(userId: string): Promise<Budget[]> {
    const now = Date.now();
    return await this.getCollection()
      .query(
        Q.where('user_id', userId),
        Q.where('start_date', Q.lte(now)),
        Q.or(
          Q.where('end_date', null),
          Q.where('end_date', Q.gte(now))
        )
      )
      .fetch();
  }

  /**
   * Get budgets exceeding their limit
   */
  async getOverBudget(userId: string): Promise<Budget[]> {
    const budgets = await this.getByUserId(userId);
    return budgets.filter((budget) => budget.spent > budget.amount);
  }

  /**
   * Update spent amount
   */
  async updateSpent(id: string, amount: number): Promise<Budget> {
    const budget = await this.getById(id);
    if (!budget) {
      throw new Error('Budget not found');
    }

    return await this.update(id, { spent: budget.spent + amount } as any);
  }

  /**
   * Get budget utilization percentage
   */
  async getUtilization(id: string): Promise<number> {
    const budget = await this.getById(id);
    if (!budget || budget.amount === 0) {
      return 0;
    }

    return (budget.spent / budget.amount) * 100;
  }
}

export default new BudgetRepository();
