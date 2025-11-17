import { MMKV } from 'react-native-mmkv';

/**
 * MMKV Storage - Fast key-value storage for settings and preferences
 * Used for: app settings, security settings, cache, session data
 */

// Main storage instance
export const storage = new MMKV({
  id: 'fincloud-storage',
  encryptionKey: 'fincloud-mmkv-key', // TODO: Generate dynamic key based on user PIN/biometric
});

// Separate storage for sensitive data
export const secureStorage = new MMKV({
  id: 'fincloud-secure',
  encryptionKey: 'fincloud-secure-key', // TODO: Use device-specific encryption key
});

/**
 * Storage utilities
 */
export const mmkvStorage = {
  // Generic methods
  set: (key: string, value: string | number | boolean): void => {
    storage.set(key, value);
  },

  get: (key: string): string | number | boolean | undefined => {
    return storage.getString(key) ?? storage.getNumber(key) ?? storage.getBoolean(key);
  },

  getString: (key: string): string | undefined => {
    return storage.getString(key);
  },

  getNumber: (key: string): number | undefined => {
    return storage.getNumber(key);
  },

  getBoolean: (key: string): boolean | undefined => {
    return storage.getBoolean(key);
  },

  delete: (key: string): void => {
    storage.delete(key);
  },

  clear: (): void => {
    storage.clearAll();
  },

  contains: (key: string): boolean => {
    return storage.contains(key);
  },

  // JSON methods
  setObject: <T>(key: string, value: T): void => {
    storage.set(key, JSON.stringify(value));
  },

  getObject: <T>(key: string): T | undefined => {
    const jsonString = storage.getString(key);
    if (!jsonString) return undefined;
    try {
      return JSON.parse(jsonString) as T;
    } catch {
      return undefined;
    }
  },
};

/**
 * Secure storage utilities (for sensitive data like tokens, PIN hash)
 */
export const mmkvSecureStorage = {
  set: (key: string, value: string): void => {
    secureStorage.set(key, value);
  },

  get: (key: string): string | undefined => {
    return secureStorage.getString(key);
  },

  delete: (key: string): void => {
    secureStorage.delete(key);
  },

  clear: (): void => {
    secureStorage.clearAll();
  },

  contains: (key: string): boolean => {
    return secureStorage.contains(key);
  },

  setObject: <T>(key: string, value: T): void => {
    secureStorage.set(key, JSON.stringify(value));
  },

  getObject: <T>(key: string): T | undefined => {
    const jsonString = secureStorage.getString(key);
    if (!jsonString) return undefined;
    try {
      return JSON.parse(jsonString) as T;
    } catch {
      return undefined;
    }
  },
};

/**
 * Storage keys constants
 */
export const StorageKeys = {
  // Auth
  AUTH_TOKENS: 'auth_tokens',
  USER_DATA: 'user_data',

  // Security
  SECURITY_SETTINGS: 'security_settings',
  PIN_HASH: 'pin_hash',
  LAST_ACTIVITY: 'last_activity',

  // App Settings
  APP_SETTINGS: 'app_settings',
  LANGUAGE: 'language',
  THEME: 'theme',
  CURRENCY: 'currency',

  // Sync
  LAST_SYNC: 'last_sync',
  PENDING_CHANGES: 'pending_changes',

  // Onboarding
  ONBOARDING_COMPLETED: 'onboarding_completed',
  FIRST_LAUNCH: 'first_launch',
} as const;
