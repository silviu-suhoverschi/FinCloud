import { categorySeedService } from './CategorySeedService';
import { recurringTransactionService } from './RecurringTransactionService';
import { notificationService } from './NotificationService';
import { mmkvStorage, StorageKeys } from '../storage/mmkv';
import i18n from '../i18n';

/**
 * Initialization Service
 * Handles app startup tasks like seeding data, checking recurring transactions, etc.
 */
class InitializationService {
  private readonly USER_ID = 'offline-user'; // Constant user ID for offline mode

  /**
   * Initialize the app on first launch
   */
  async initializeApp(): Promise<void> {
    console.log('Initializing FinCloud app...');

    try {
      // Check if this is first launch
      const isFirstLaunch = !mmkvStorage.contains(StorageKeys.FIRST_LAUNCH);

      if (isFirstLaunch) {
        console.log('First launch detected, setting up app...');
        mmkvStorage.set(StorageKeys.FIRST_LAUNCH, false);

        // Set default settings
        await this.setDefaultSettings();
      }

      // Seed categories if not already seeded
      await this.seedCategoriesIfNeeded();

      // Request notification permissions
      await notificationService.requestPermissions();

      // Process recurring transactions
      await this.processRecurringTransactions();

      console.log('App initialization complete');
    } catch (error) {
      console.error('Error initializing app:', error);
      throw error;
    }
  }

  /**
   * Set default app settings
   */
  private async setDefaultSettings(): Promise<void> {
    const defaultSettings = {
      language: 'en',
      currency: 'USD',
      theme: 'auto',
      notificationsEnabled: true,
      biometricEnabled: false,
      autoLockTimeout: 300000, // 5 minutes
      syncEnabled: false,
      syncWifiOnly: true,
    };

    mmkvStorage.setObject(StorageKeys.APP_SETTINGS, defaultSettings);
    mmkvStorage.set(StorageKeys.LANGUAGE, 'en');
    mmkvStorage.set(StorageKeys.CURRENCY, 'USD');
    mmkvStorage.set(StorageKeys.THEME, 'auto');

    console.log('Default settings configured');
  }

  /**
   * Seed preset categories if not already seeded
   */
  private async seedCategoriesIfNeeded(): Promise<void> {
    if (categorySeedService.hasSeeded()) {
      console.log('Categories already seeded');
      return;
    }

    // Get current language
    const language = i18n.language || 'en';
    const lang = language.startsWith('ro') ? 'ro' : 'en';

    console.log(`Seeding categories in ${lang}...`);
    const count = await categorySeedService.seedCategories(this.USER_ID, lang);
    console.log(`Seeded ${count} preset categories`);
  }

  /**
   * Process recurring transactions that are due
   */
  private async processRecurringTransactions(): Promise<void> {
    try {
      const count = await recurringTransactionService.processRecurringTransactions(
        this.USER_ID
      );
      if (count > 0) {
        console.log(`Processed ${count} recurring transactions`);
      }
    } catch (error) {
      console.error('Error processing recurring transactions:', error);
    }
  }

  /**
   * Complete onboarding
   */
  async completeOnboarding(): Promise<void> {
    mmkvStorage.set(StorageKeys.HAS_COMPLETED_ONBOARDING, true);
    mmkvStorage.set(StorageKeys.ONBOARDING_COMPLETED, true);
    console.log('Onboarding completed');
  }

  /**
   * Check if user has completed onboarding
   */
  hasCompletedOnboarding(): boolean {
    return (
      mmkvStorage.getBoolean(StorageKeys.HAS_COMPLETED_ONBOARDING) ||
      mmkvStorage.getBoolean(StorageKeys.ONBOARDING_COMPLETED) ||
      false
    );
  }

  /**
   * Reset app data (for testing/development)
   */
  async resetAppData(): Promise<void> {
    console.warn('Resetting all app data...');

    // Clear MMKV storage
    mmkvStorage.clear();

    // Reset category seeding status
    categorySeedService.resetSeedingStatus();

    // Clear database (would need to implement in database service)
    // For now, just log
    console.warn('Database reset not implemented - requires app restart');
  }

  /**
   * Get app version info
   */
  getAppVersion(): string {
    return '1.0.0'; // TODO: Get from package.json or app config
  }

  /**
   * Daily maintenance tasks
   */
  async performDailyMaintenance(): Promise<void> {
    console.log('Running daily maintenance...');

    try {
      // Process recurring transactions
      await this.processRecurringTransactions();

      // Check budget alerts
      await notificationService.checkBudgetAlerts(this.USER_ID);

      // Update last maintenance timestamp
      mmkvStorage.set('last_maintenance', Date.now());

      console.log('Daily maintenance complete');
    } catch (error) {
      console.error('Error during daily maintenance:', error);
    }
  }

  /**
   * Check if daily maintenance is needed
   */
  shouldPerformDailyMaintenance(): boolean {
    const lastMaintenance = mmkvStorage.getNumber('last_maintenance');

    if (!lastMaintenance) {
      return true;
    }

    const oneDayAgo = Date.now() - 24 * 60 * 60 * 1000;
    return lastMaintenance < oneDayAgo;
  }
}

export const initializationService = new InitializationService();
export const USER_ID = 'offline-user'; // Export for use in screens
