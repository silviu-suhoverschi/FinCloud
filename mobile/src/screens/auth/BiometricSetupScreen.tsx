import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import { useTranslation } from 'react-i18next';
import { StackNavigationProp } from '@react-navigation/stack';
import { AuthStackParamList } from '../../navigation/types';
import { mmkvSecureStorage, StorageKeys } from '../../storage/mmkv';
import * as LocalAuthentication from 'expo-local-authentication';
import { BiometricType } from '../../types';

type BiometricSetupScreenNavigationProp = StackNavigationProp<
  AuthStackParamList,
  'BiometricSetup'
>;

interface Props {
  navigation: BiometricSetupScreenNavigationProp;
}

export default function BiometricSetupScreen({ navigation }: Props) {
  const { t } = useTranslation();
  const [biometricType, setBiometricType] = useState<BiometricType>('none');
  const [isAvailable, setIsAvailable] = useState(false);
  const [isEnrolled, setIsEnrolled] = useState(false);

  useEffect(() => {
    checkBiometricAvailability();
  }, []);

  const checkBiometricAvailability = async () => {
    try {
      const compatible = await LocalAuthentication.hasHardwareAsync();
      const enrolled = await LocalAuthentication.isEnrolledAsync();

      setIsAvailable(compatible);
      setIsEnrolled(enrolled);

      if (compatible) {
        const types = await LocalAuthentication.supportedAuthenticationTypesAsync();

        if (types.includes(LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION)) {
          setBiometricType('face');
        } else if (types.includes(LocalAuthentication.AuthenticationType.FINGERPRINT)) {
          setBiometricType('fingerprint');
        } else if (types.includes(LocalAuthentication.AuthenticationType.IRIS)) {
          setBiometricType('iris');
        }
      }
    } catch (error) {
      console.error('Error checking biometric availability:', error);
    }
  };

  const handleEnableBiometric = async () => {
    try {
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Verify your identity',
        fallbackLabel: 'Use PIN instead',
        disableDeviceFallback: false,
      });

      if (result.success) {
        const settings = mmkvSecureStorage.getObject<any>(StorageKeys.SECURITY_SETTINGS) || {};
        mmkvSecureStorage.setObject(StorageKeys.SECURITY_SETTINGS, {
          ...settings,
          biometricEnabled: true,
        });

        Alert.alert(
          'Success',
          'Biometric authentication has been enabled',
          [{ text: 'OK', onPress: handleComplete }]
        );
      } else {
        Alert.alert('Failed', 'Biometric authentication failed. Please try again.');
      }
    } catch (error) {
      console.error('Error enabling biometric:', error);
      Alert.alert('Error', 'An error occurred while enabling biometric authentication');
    }
  };

  const handleSkip = () => {
    Alert.alert(
      'Skip Biometric Setup',
      'You can enable biometric authentication later in Security settings',
      [
        { text: 'Go Back', style: 'cancel' },
        { text: 'Skip', onPress: handleComplete, style: 'destructive' },
      ]
    );
  };

  const handleComplete = () => {
    // Mark onboarding as completed
    mmkvSecureStorage.set(StorageKeys.ONBOARDING_COMPLETED, 'true');
    mmkvSecureStorage.set(StorageKeys.FIRST_LAUNCH, 'false');

    // Navigate to main app (handled by root navigator based on onboarding status)
    // For now, just show an alert
    Alert.alert('Setup Complete', 'Your FinCloud account is ready!');
  };

  const getBiometricIcon = () => {
    switch (biometricType) {
      case 'face':
        return '🤳';
      case 'fingerprint':
        return '👆';
      case 'iris':
        return '👁️';
      default:
        return '🔒';
    }
  };

  const getBiometricName = () => {
    switch (biometricType) {
      case 'face':
        return 'Face Recognition';
      case 'fingerprint':
        return 'Fingerprint';
      case 'iris':
        return 'Iris Recognition';
      default:
        return 'Biometric';
    }
  };

  if (!isAvailable || !isEnrolled) {
    return (
      <View style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.icon}>🔒</Text>
          <Text style={styles.title}>Biometric Not Available</Text>
          <Text style={styles.description}>
            {!isAvailable
              ? 'Your device does not support biometric authentication.'
              : 'No biometric data is enrolled on this device. Please set up biometric authentication in your device settings first.'}
          </Text>
        </View>
        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={styles.primaryButton}
            onPress={handleComplete}
          >
            <Text style={styles.primaryButtonText}>Continue</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.icon}>{getBiometricIcon()}</Text>
        <Text style={styles.title}>Enable {getBiometricName()}</Text>
        <Text style={styles.description}>
          Use {getBiometricName().toLowerCase()} to quickly and securely unlock
          FinCloud without entering your PIN.
        </Text>

        <View style={styles.features}>
          <View style={styles.feature}>
            <Text style={styles.featureIcon}>⚡</Text>
            <Text style={styles.featureText}>Quick & convenient unlock</Text>
          </View>
          <View style={styles.feature}>
            <Text style={styles.featureIcon}>🔐</Text>
            <Text style={styles.featureText}>Extra layer of security</Text>
          </View>
          <View style={styles.feature}>
            <Text style={styles.featureIcon}>🔒</Text>
            <Text style={styles.featureText}>Your data stays encrypted</Text>
          </View>
        </View>
      </View>

      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={styles.primaryButton}
          onPress={handleEnableBiometric}
        >
          <Text style={styles.primaryButtonText}>Enable {getBiometricName()}</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.secondaryButton} onPress={handleSkip}>
          <Text style={styles.secondaryButtonText}>Skip for Now</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  icon: {
    fontSize: 80,
    marginBottom: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
    textAlign: 'center',
  },
  description: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32,
  },
  features: {
    width: '100%',
  },
  feature: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  featureIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  featureText: {
    fontSize: 16,
    color: '#444',
  },
  buttonContainer: {
    padding: 24,
  },
  primaryButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  primaryButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  secondaryButton: {
    paddingVertical: 16,
    alignItems: 'center',
  },
  secondaryButtonText: {
    color: '#007AFF',
    fontSize: 16,
    fontWeight: '600',
  },
});
