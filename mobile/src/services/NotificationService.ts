import { budgetRepository, transactionRepository } from '../repositories';
import * as Notifications from 'expo-notifications';
import { mmkvStorage, StorageKeys } from '../storage/mmkv';

// Configure notification behavior
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

export interface BudgetAlert {
  budgetId: string;
  categoryName: string;
  spent: number;
  budgetAmount: number;
  percentage: number;
}

class NotificationService {
  /**
   * Request notification permissions
   */
  async requestPermissions(): Promise<boolean> {
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;

    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }

    return finalStatus === 'granted';
  }

  /**
   * Check if notifications are enabled in settings
   */
  areNotificationsEnabled(): boolean {
    const settings = mmkvStorage.getObject<any>(StorageKeys.APP_SETTINGS);
    return settings?.notificationsEnabled !== false; // Default to true
  }

  /**
   * Send a local notification
   */
  async sendNotification(
    title: string,
    body: string,
    data?: Record<string, any>
  ): Promise<string | null> {
    if (!this.areNotificationsEnabled()) {
      return null;
    }

    const hasPermission = await this.requestPermissions();
    if (!hasPermission) {
      console.log('Notification permissions not granted');
      return null;
    }

    try {
      const notificationId = await Notifications.scheduleNotificationAsync({
        content: {
          title,
          body,
          data,
          sound: true,
        },
        trigger: null, // Send immediately
      });

      return notificationId;
    } catch (error) {
      console.error('Error sending notification:', error);
      return null;
    }
  }

  /**
   * Check budgets and send overspending notifications
   */
  async checkBudgetAlerts(userId: string): Promise<BudgetAlert[]> {
    const alerts: BudgetAlert[] = [];

    try {
      const budgets = await budgetRepository.getByUserId(userId);
      const now = new Date();

      for (const budget of budgets) {
        // Check if budget is active
        if (
          budget.startDate > now ||
          (budget.endDate && budget.endDate < now)
        ) {
          continue;
        }

        // Calculate spent percentage
        const percentage = (budget.spent / budget.amount) * 100;

        // Alert thresholds: 80%, 100%, 120%
        const shouldAlert =
          percentage >= 80 && percentage < 85 // 80-85%
            ? 80
            : percentage >= 100 && percentage < 105 // 100-105%
              ? 100
              : percentage >= 120 && percentage < 125 // 120-125%
                ? 120
                : null;

        if (shouldAlert) {
          const alert: BudgetAlert = {
            budgetId: budget.id,
            categoryName: budget.categoryId || 'General',
            spent: budget.spent,
            budgetAmount: budget.amount,
            percentage,
          };

          alerts.push(alert);

          // Send notification
          let title = '';
          let body = '';

          if (shouldAlert === 80) {
            title = '⚠️ Budget Warning';
            body = `You've used ${Math.round(percentage)}% of your ${alert.categoryName} budget`;
          } else if (shouldAlert === 100) {
            title = '🚨 Budget Exceeded';
            body = `You've reached your ${alert.categoryName} budget limit!`;
          } else if (shouldAlert === 120) {
            title = '🚨 Budget Overspent';
            body = `You're ${Math.round(percentage - 100)}% over your ${alert.categoryName} budget`;
          }

          await this.sendNotification(title, body, {
            type: 'budget_alert',
            budgetId: budget.id,
            percentage,
          });
        }
      }
    } catch (error) {
      console.error('Error checking budget alerts:', error);
    }

    return alerts;
  }

  /**
   * Update budget spent amount after transaction
   */
  async updateBudgetSpent(
    userId: string,
    categoryId: string | undefined,
    amount: number,
    type: 'income' | 'expense' | 'transfer'
  ): Promise<void> {
    if (type !== 'expense' || !categoryId) {
      return;
    }

    try {
      const budgets = await budgetRepository.getByUserId(userId);
      const now = new Date();

      for (const budget of budgets) {
        // Check if this budget applies to the category
        if (budget.categoryId !== categoryId) {
          continue;
        }

        // Check if budget is active
        if (
          budget.startDate > now ||
          (budget.endDate && budget.endDate < now)
        ) {
          continue;
        }

        // Update spent amount
        const newSpent = budget.spent + amount;
        await budgetRepository.updateSpent(budget.id, newSpent);
      }

      // Check for alerts after updating
      await this.checkBudgetAlerts(userId);
    } catch (error) {
      console.error('Error updating budget spent:', error);
    }
  }

  /**
   * Schedule a notification for recurring transaction
   */
  async scheduleRecurringTransactionNotification(
    transactionDescription: string,
    triggerDate: Date
  ): Promise<string | null> {
    if (!this.areNotificationsEnabled()) {
      return null;
    }

    const hasPermission = await this.requestPermissions();
    if (!hasPermission) {
      return null;
    }

    try {
      const notificationId = await Notifications.scheduleNotificationAsync({
        content: {
          title: '💸 Recurring Transaction',
          body: `Reminder: ${transactionDescription}`,
          data: { type: 'recurring_transaction' },
        },
        trigger: triggerDate,
      });

      return notificationId;
    } catch (error) {
      console.error('Error scheduling notification:', error);
      return null;
    }
  }

  /**
   * Cancel a scheduled notification
   */
  async cancelNotification(notificationId: string): Promise<void> {
    try {
      await Notifications.cancelScheduledNotificationAsync(notificationId);
    } catch (error) {
      console.error('Error canceling notification:', error);
    }
  }

  /**
   * Cancel all scheduled notifications
   */
  async cancelAllNotifications(): Promise<void> {
    try {
      await Notifications.cancelAllScheduledNotificationsAsync();
    } catch (error) {
      console.error('Error canceling all notifications:', error);
    }
  }
}

export const notificationService = new NotificationService();
