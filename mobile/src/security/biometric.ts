import * as LocalAuthentication from 'expo-local-authentication';
import { BiometricType } from '../types';
import { mmkvSecureStorage, StorageKeys } from '../storage/mmkv';
import { getSecuritySettings, updateSecuritySettings } from './pin';

/**
 * Biometric Authentication (Face ID, Touch ID, Fingerprint)
 */

/**
 * Check if device supports biometric authentication
 */
export const isBiometricSupported = async (): Promise<boolean> => {
  try {
    const compatible = await LocalAuthentication.hasHardwareAsync();
    return compatible;
  } catch (error) {
    console.error('Error checking biometric support:', error);
    return false;
  }
};

/**
 * Check if biometric authentication is enrolled
 */
export const isBiometricEnrolled = async (): Promise<boolean> => {
  try {
    const enrolled = await LocalAuthentication.isEnrolledAsync();
    return enrolled;
  } catch (error) {
    console.error('Error checking biometric enrollment:', error);
    return false;
  }
};

/**
 * Get available biometric types
 */
export const getAvailableBiometricTypes = async (): Promise<BiometricType[]> => {
  try {
    const types = await LocalAuthentication.supportedAuthenticationTypesAsync();
    const biometricTypes: BiometricType[] = [];

    types.forEach((type) => {
      switch (type) {
        case LocalAuthentication.AuthenticationType.FINGERPRINT:
          biometricTypes.push('fingerprint');
          break;
        case LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION:
          biometricTypes.push('face');
          break;
        case LocalAuthentication.AuthenticationType.IRIS:
          biometricTypes.push('iris');
          break;
      }
    });

    return biometricTypes.length > 0 ? biometricTypes : ['none'];
  } catch (error) {
    console.error('Error getting biometric types:', error);
    return ['none'];
  }
};

/**
 * Get biometric type name for display
 */
export const getBiometricTypeName = (type: BiometricType): string => {
  switch (type) {
    case 'fingerprint':
      return 'Fingerprint';
    case 'face':
      return 'Face ID';
    case 'iris':
      return 'Iris';
    default:
      return 'Biometric';
  }
};

/**
 * Authenticate with biometrics
 */
export const authenticateWithBiometrics = async (
  promptMessage: string = 'Authenticate to continue'
): Promise<{ success: boolean; error?: string }> => {
  try {
    // Check if biometric is available
    const isSupported = await isBiometricSupported();
    if (!isSupported) {
      return { success: false, error: 'Biometric authentication not supported' };
    }

    const isEnrolled = await isBiometricEnrolled();
    if (!isEnrolled) {
      return { success: false, error: 'No biometric credentials enrolled' };
    }

    // Authenticate
    const result = await LocalAuthentication.authenticateAsync({
      promptMessage,
      cancelLabel: 'Cancel',
      disableDeviceFallback: false,
      fallbackLabel: 'Use PIN',
    });

    if (result.success) {
      return { success: true };
    } else {
      return {
        success: false,
        error: result.error || 'Authentication failed'
      };
    }
  } catch (error) {
    console.error('Error authenticating with biometrics:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Authentication error'
    };
  }
};

/**
 * Enable biometric authentication
 */
export const enableBiometric = async (): Promise<{ success: boolean; error?: string }> => {
  try {
    // Check if biometric is available
    const isSupported = await isBiometricSupported();
    if (!isSupported) {
      return { success: false, error: 'Biometric authentication not supported on this device' };
    }

    const isEnrolled = await isBiometricEnrolled();
    if (!isEnrolled) {
      return { success: false, error: 'Please enroll biometric credentials in device settings first' };
    }

    // Test authentication
    const authResult = await authenticateWithBiometrics('Enable biometric authentication');
    if (!authResult.success) {
      return authResult;
    }

    // Update settings
    updateSecuritySettings({ biometricEnabled: true });

    return { success: true };
  } catch (error) {
    console.error('Error enabling biometric:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to enable biometric'
    };
  }
};

/**
 * Disable biometric authentication
 */
export const disableBiometric = (): void => {
  updateSecuritySettings({ biometricEnabled: false });
};

/**
 * Check if biometric is enabled
 */
export const isBiometricEnabled = (): boolean => {
  const settings = getSecuritySettings();
  return settings.biometricEnabled;
};

/**
 * Get biometric status info
 */
export const getBiometricStatus = async (): Promise<{
  supported: boolean;
  enrolled: boolean;
  enabled: boolean;
  types: BiometricType[];
}> => {
  const supported = await isBiometricSupported();
  const enrolled = supported ? await isBiometricEnrolled() : false;
  const enabled = isBiometricEnabled();
  const types = supported ? await getAvailableBiometricTypes() : ['none'];

  return {
    supported,
    enrolled,
    enabled,
    types,
  };
};

export const BiometricService = {
  isBiometricSupported,
  isBiometricEnrolled,
  getAvailableBiometricTypes,
  getBiometricTypeName,
  authenticateWithBiometrics,
  enableBiometric,
  disableBiometric,
  isBiometricEnabled,
  getBiometricStatus,
};
