import { transactionRepository } from '../repositories';
import { TransactionType } from '../types';

export interface RecurringPattern {
  frequency: 'daily' | 'weekly' | 'monthly' | 'yearly';
  interval: number; // e.g., every 2 weeks = { frequency: 'weekly', interval: 2 }
  startDate: Date;
  endDate?: Date; // Optional, recurring until stopped if not set
  dayOfWeek?: number; // 0-6 for weekly (0 = Sunday)
  dayOfMonth?: number; // 1-31 for monthly
  monthOfYear?: number; // 1-12 for yearly
}

export interface RecurringTransaction {
  id: string;
  userId: string;
  accountId: string;
  type: TransactionType;
  amount: number;
  currency: string;
  description: string;
  categoryId?: string;
  tags: string[];
  attachments: string[];
  destinationAccountId?: string;
  pattern: RecurringPattern;
  lastExecuted?: Date;
  nextExecution: Date;
  isActive: boolean;
}

class RecurringTransactionService {
  private recurringTransactions: Map<string, RecurringTransaction> = new Map();

  /**
   * Load recurring transactions from storage
   */
  async loadRecurringTransactions(userId: string): Promise<RecurringTransaction[]> {
    // In production, load from database
    // For now, return from memory
    return Array.from(this.recurringTransactions.values()).filter(
      (rt) => rt.userId === userId
    );
  }

  /**
   * Add a new recurring transaction
   */
  async addRecurringTransaction(
    recurringTransaction: Omit<RecurringTransaction, 'id' | 'nextExecution'>
  ): Promise<RecurringTransaction> {
    const id = `recurring_${Date.now()}_${Math.random().toString(36).substring(7)}`;
    const nextExecution = this.calculateNextExecution(
      recurringTransaction.pattern,
      recurringTransaction.lastExecuted
    );

    const newRecurring: RecurringTransaction = {
      ...recurringTransaction,
      id,
      nextExecution,
    };

    this.recurringTransactions.set(id, newRecurring);
    return newRecurring;
  }

  /**
   * Calculate the next execution date based on pattern
   */
  calculateNextExecution(
    pattern: RecurringPattern,
    lastExecuted?: Date
  ): Date {
    const baseDate = lastExecuted || pattern.startDate;
    const next = new Date(baseDate);

    switch (pattern.frequency) {
      case 'daily':
        next.setDate(next.getDate() + pattern.interval);
        break;

      case 'weekly':
        next.setDate(next.getDate() + 7 * pattern.interval);
        if (pattern.dayOfWeek !== undefined) {
          // Adjust to specific day of week
          const currentDay = next.getDay();
          const diff = (pattern.dayOfWeek - currentDay + 7) % 7;
          next.setDate(next.getDate() + diff);
        }
        break;

      case 'monthly':
        next.setMonth(next.getMonth() + pattern.interval);
        if (pattern.dayOfMonth !== undefined) {
          // Handle cases where day doesn't exist in month (e.g., Feb 31)
          const maxDay = new Date(next.getFullYear(), next.getMonth() + 1, 0).getDate();
          next.setDate(Math.min(pattern.dayOfMonth, maxDay));
        }
        break;

      case 'yearly':
        next.setFullYear(next.getFullYear() + pattern.interval);
        if (pattern.monthOfYear !== undefined) {
          next.setMonth(pattern.monthOfYear - 1);
        }
        if (pattern.dayOfMonth !== undefined) {
          next.setDate(pattern.dayOfMonth);
        }
        break;
    }

    return next;
  }

  /**
   * Check and execute due recurring transactions
   */
  async processRecurringTransactions(userId: string): Promise<number> {
    const now = new Date();
    let executedCount = 0;

    for (const [id, recurring] of this.recurringTransactions.entries()) {
      if (
        recurring.userId !== userId ||
        !recurring.isActive ||
        recurring.nextExecution > now
      ) {
        continue;
      }

      // Check if we've passed the end date
      if (recurring.pattern.endDate && now > recurring.pattern.endDate) {
        recurring.isActive = false;
        this.recurringTransactions.set(id, recurring);
        continue;
      }

      try {
        // Create the actual transaction
        await transactionRepository.create({
          userId: recurring.userId,
          accountId: recurring.accountId,
          type: recurring.type,
          amount: recurring.amount,
          currency: recurring.currency,
          description: recurring.description,
          date: now,
          categoryId: recurring.categoryId,
          tags: recurring.tags,
          recurring: true,
          recurringId: id,
          attachments: recurring.attachments,
          destinationAccountId: recurring.destinationAccountId,
        });

        // Update recurring transaction
        recurring.lastExecuted = now;
        recurring.nextExecution = this.calculateNextExecution(
          recurring.pattern,
          now
        );
        this.recurringTransactions.set(id, recurring);

        executedCount++;
      } catch (error) {
        console.error(`Error processing recurring transaction ${id}:`, error);
      }
    }

    return executedCount;
  }

  /**
   * Update a recurring transaction
   */
  async updateRecurringTransaction(
    id: string,
    updates: Partial<RecurringTransaction>
  ): Promise<RecurringTransaction | null> {
    const existing = this.recurringTransactions.get(id);
    if (!existing) {
      return null;
    }

    const updated = { ...existing, ...updates };

    // Recalculate next execution if pattern changed
    if (updates.pattern) {
      updated.nextExecution = this.calculateNextExecution(
        updated.pattern,
        updated.lastExecuted
      );
    }

    this.recurringTransactions.set(id, updated);
    return updated;
  }

  /**
   * Delete a recurring transaction
   */
  async deleteRecurringTransaction(id: string): Promise<boolean> {
    return this.recurringTransactions.delete(id);
  }

  /**
   * Get a recurring transaction by ID
   */
  async getRecurringTransaction(id: string): Promise<RecurringTransaction | null> {
    return this.recurringTransactions.get(id) || null;
  }

  /**
   * Get all active recurring transactions for a user
   */
  async getActiveRecurringTransactions(userId: string): Promise<RecurringTransaction[]> {
    return Array.from(this.recurringTransactions.values()).filter(
      (rt) => rt.userId === userId && rt.isActive
    );
  }
}

export const recurringTransactionService = new RecurringTransactionService();
