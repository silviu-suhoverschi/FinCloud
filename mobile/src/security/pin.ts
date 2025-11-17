import { mmkvSecureStorage, StorageKeys } from '../storage/mmkv';
import { SecuritySettings } from '../types';
import { hashPIN, verifyPIN } from './encryption';

/**
 * PIN Lock System
 * Supports 4, 6, or 8 digit PINs
 */

const DEFAULT_SECURITY_SETTINGS: SecuritySettings = {
  pinEnabled: false,
  pinLength: 4,
  biometricEnabled: false,
  autoLockTimeout: 60, // 60 seconds default
  lastActivityTimestamp: Date.now(),
};

/**
 * Set up a new PIN
 */
export const setupPIN = async (pin: string, length: 4 | 6 | 8 = 4): Promise<boolean> => {
  try {
    // Validate PIN
    if (!validatePIN(pin, length)) {
      throw new Error(`PIN must be exactly ${length} digits`);
    }

    // Hash the PIN
    const { hash, salt } = await hashPIN(pin);

    // Store hashed PIN and salt
    mmkvSecureStorage.setObject(StorageKeys.PIN_HASH, { hash, salt });

    // Update security settings
    const settings = getSecuritySettings();
    settings.pinEnabled = true;
    settings.pinLength = length;
    mmkvSecureStorage.setObject(StorageKeys.SECURITY_SETTINGS, settings);

    return true;
  } catch (error) {
    console.error('Error setting up PIN:', error);
    return false;
  }
};

/**
 * Verify a PIN
 */
export const verifyPINCode = async (pin: string): Promise<boolean> => {
  try {
    const pinData = mmkvSecureStorage.getObject<{ hash: string; salt: string }>(StorageKeys.PIN_HASH);

    if (!pinData) {
      throw new Error('No PIN configured');
    }

    const isValid = await verifyPIN(pin, pinData.hash, pinData.salt);

    if (isValid) {
      updateLastActivity();
    }

    return isValid;
  } catch (error) {
    console.error('Error verifying PIN:', error);
    return false;
  }
};

/**
 * Change PIN
 */
export const changePIN = async (oldPin: string, newPin: string): Promise<boolean> => {
  try {
    // Verify old PIN
    const isOldPinValid = await verifyPINCode(oldPin);
    if (!isOldPinValid) {
      throw new Error('Invalid current PIN');
    }

    // Get current settings for PIN length
    const settings = getSecuritySettings();

    // Validate new PIN
    if (!validatePIN(newPin, settings.pinLength)) {
      throw new Error(`New PIN must be exactly ${settings.pinLength} digits`);
    }

    // Hash the new PIN
    const { hash, salt } = await hashPIN(newPin);

    // Store new hashed PIN
    mmkvSecureStorage.setObject(StorageKeys.PIN_HASH, { hash, salt });

    return true;
  } catch (error) {
    console.error('Error changing PIN:', error);
    return false;
  }
};

/**
 * Disable PIN
 */
export const disablePIN = async (pin: string): Promise<boolean> => {
  try {
    // Verify PIN before disabling
    const isValid = await verifyPINCode(pin);
    if (!isValid) {
      throw new Error('Invalid PIN');
    }

    // Remove PIN hash
    mmkvSecureStorage.delete(StorageKeys.PIN_HASH);

    // Update security settings
    const settings = getSecuritySettings();
    settings.pinEnabled = false;
    mmkvSecureStorage.setObject(StorageKeys.SECURITY_SETTINGS, settings);

    return true;
  } catch (error) {
    console.error('Error disabling PIN:', error);
    return false;
  }
};

/**
 * Check if PIN is enabled
 */
export const isPINEnabled = (): boolean => {
  const settings = getSecuritySettings();
  return settings.pinEnabled && mmkvSecureStorage.contains(StorageKeys.PIN_HASH);
};

/**
 * Validate PIN format
 */
export const validatePIN = (pin: string, length: 4 | 6 | 8): boolean => {
  const pinRegex = new RegExp(`^\\d{${length}}$`);
  return pinRegex.test(pin);
};

/**
 * Get security settings
 */
export const getSecuritySettings = (): SecuritySettings => {
  const settings = mmkvSecureStorage.getObject<SecuritySettings>(StorageKeys.SECURITY_SETTINGS);
  return settings || DEFAULT_SECURITY_SETTINGS;
};

/**
 * Update security settings
 */
export const updateSecuritySettings = (settings: Partial<SecuritySettings>): void => {
  const currentSettings = getSecuritySettings();
  const newSettings = { ...currentSettings, ...settings };
  mmkvSecureStorage.setObject(StorageKeys.SECURITY_SETTINGS, newSettings);
};

/**
 * Update last activity timestamp
 */
export const updateLastActivity = (): void => {
  const settings = getSecuritySettings();
  settings.lastActivityTimestamp = Date.now();
  mmkvSecureStorage.setObject(StorageKeys.SECURITY_SETTINGS, settings);
};

/**
 * Check if app should be locked based on auto-lock timeout
 */
export const shouldLockApp = (): boolean => {
  const settings = getSecuritySettings();

  // If auto-lock is disabled (timeout = 0)
  if (settings.autoLockTimeout === 0) {
    return false;
  }

  // If PIN is not enabled
  if (!isPINEnabled()) {
    return false;
  }

  const timeSinceLastActivity = Date.now() - settings.lastActivityTimestamp;
  const timeoutMs = settings.autoLockTimeout * 1000;

  return timeSinceLastActivity >= timeoutMs;
};

/**
 * Get time until auto-lock (in seconds)
 */
export const getTimeUntilLock = (): number => {
  const settings = getSecuritySettings();

  if (settings.autoLockTimeout === 0 || !isPINEnabled()) {
    return -1; // Auto-lock disabled
  }

  const timeSinceLastActivity = Date.now() - settings.lastActivityTimestamp;
  const timeoutMs = settings.autoLockTimeout * 1000;
  const remainingTime = Math.max(0, timeoutMs - timeSinceLastActivity);

  return Math.floor(remainingTime / 1000);
};

export const PINService = {
  setupPIN,
  verifyPINCode,
  changePIN,
  disablePIN,
  isPINEnabled,
  validatePIN,
  getSecuritySettings,
  updateSecuritySettings,
  updateLastActivity,
  shouldLockApp,
  getTimeUntilLock,
};
