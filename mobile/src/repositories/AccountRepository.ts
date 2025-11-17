import { Q } from '@nozbe/watermelondb';
import { BaseRepository } from './BaseRepository';
import Account from '../models/Account';
import { AccountType } from '../types';

export class AccountRepository extends BaseRepository<Account> {
  constructor() {
    super('accounts');
  }

  /**
   * Get accounts by type
   */
  async getByType(userId: string, type: AccountType): Promise<Account[]> {
    return await this.getCollection()
      .query(
        Q.where('user_id', userId),
        Q.where('type', type)
      )
      .fetch();
  }

  /**
   * Get active accounts
   */
  async getActive(userId: string): Promise<Account[]> {
    return await this.getCollection()
      .query(
        Q.where('user_id', userId),
        Q.where('is_active', true)
      )
      .fetch();
  }

  /**
   * Get accounts by currency
   */
  async getByCurrency(userId: string, currency: string): Promise<Account[]> {
    return await this.getCollection()
      .query(
        Q.where('user_id', userId),
        Q.where('currency', currency)
      )
      .fetch();
  }

  /**
   * Get total balance by currency
   */
  async getTotalBalance(userId: string, currency?: string): Promise<number> {
    const query = currency
      ? this.getCollection().query(
          Q.where('user_id', userId),
          Q.where('currency', currency),
          Q.where('is_active', true)
        )
      : this.getCollection().query(
          Q.where('user_id', userId),
          Q.where('is_active', true)
        );

    const accounts = await query.fetch();
    return accounts.reduce((sum, account) => sum + account.balance, 0);
  }

  /**
   * Update account balance
   */
  async updateBalance(id: string, amount: number): Promise<Account> {
    const account = await this.getById(id);
    if (!account) {
      throw new Error('Account not found');
    }

    return await this.update(id, { balance: account.balance + amount } as any);
  }

  /**
   * Deactivate account
   */
  async deactivate(id: string): Promise<Account> {
    return await this.update(id, { isActive: false } as any);
  }

  /**
   * Activate account
   */
  async activate(id: string): Promise<Account> {
    return await this.update(id, { isActive: true } as any);
  }
}

export default new AccountRepository();
