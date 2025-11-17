import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Vibration,
  AppState,
  AppStateStatus,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { mmkvSecureStorage, StorageKeys } from '../../storage/mmkv';
import * as LocalAuthentication from 'expo-local-authentication';
import * as Crypto from 'expo-crypto';

interface Props {
  onUnlock: () => void;
}

export default function LockScreen({ onUnlock }: Props) {
  const { t } = useTranslation();
  const [pin, setPin] = useState('');
  const [error, setError] = useState('');
  const [pinLength, setPinLength] = useState<4 | 6 | 8>(6);
  const [biometricEnabled, setBiometricEnabled] = useState(false);
  const [failedAttempts, setFailedAttempts] = useState(0);

  useEffect(() => {
    loadSecuritySettings();
    attemptBiometricAuth();

    const subscription = AppState.addEventListener('change', handleAppStateChange);
    return () => subscription.remove();
  }, []);

  const loadSecuritySettings = () => {
    const settings = mmkvSecureStorage.getObject<any>(StorageKeys.SECURITY_SETTINGS);
    if (settings) {
      setPinLength(settings.pinLength || 6);
      setBiometricEnabled(settings.biometricEnabled || false);
    }
  };

  const handleAppStateChange = (nextAppState: AppStateStatus) => {
    if (nextAppState === 'active' && biometricEnabled) {
      attemptBiometricAuth();
    }
  };

  const attemptBiometricAuth = async () => {
    if (!biometricEnabled) return;

    try {
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Unlock FinCloud',
        fallbackLabel: 'Use PIN',
        disableDeviceFallback: false,
      });

      if (result.success) {
        handleSuccessfulUnlock();
      }
    } catch (error) {
      console.error('Biometric auth error:', error);
    }
  };

  const handleNumberPress = (num: string) => {
    setError('');

    if (pin.length < pinLength) {
      const newPin = pin + num;
      setPin(newPin);

      if (newPin.length === pinLength) {
        setTimeout(() => verifyPin(newPin), 300);
      }
    }
  };

  const handleDelete = () => {
    setError('');
    setPin(pin.slice(0, -1));
  };

  const verifyPin = async (enteredPin: string) => {
    const storedPinHash = mmkvSecureStorage.get(StorageKeys.PIN_HASH);
    const enteredPinHash = await Crypto.digestStringAsync(
      Crypto.CryptoDigestAlgorithm.SHA256,
      enteredPin
    );

    if (enteredPinHash === storedPinHash) {
      handleSuccessfulUnlock();
    } else {
      const newFailedAttempts = failedAttempts + 1;
      setFailedAttempts(newFailedAttempts);
      setError(`Incorrect PIN. ${3 - newFailedAttempts} attempts remaining.`);
      Vibration.vibrate(500);
      setPin('');

      if (newFailedAttempts >= 3) {
        setError('Too many failed attempts. Please try again in 30 seconds.');
        setTimeout(() => {
          setFailedAttempts(0);
          setError('');
        }, 30000);
      }
    }
  };

  const handleSuccessfulUnlock = () => {
    mmkvSecureStorage.set(StorageKeys.LAST_ACTIVITY, Date.now().toString());
    setFailedAttempts(0);
    setError('');
    onUnlock();
  };

  const renderDots = () => {
    const dots = [];

    for (let i = 0; i < pinLength; i++) {
      dots.push(
        <View
          key={i}
          style={[
            styles.dot,
            i < pin.length && styles.dotFilled,
          ]}
        />
      );
    }

    return <View style={styles.dotsContainer}>{dots}</View>;
  };

  const renderNumberPad = () => {
    const isDisabled = failedAttempts >= 3;

    return (
      <View style={styles.numberPad}>
        {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((num) => (
          <TouchableOpacity
            key={num}
            style={[styles.numberButton, isDisabled && styles.numberButtonDisabled]}
            onPress={() => handleNumberPress(num.toString())}
            disabled={isDisabled}
          >
            <Text style={[styles.numberText, isDisabled && styles.numberTextDisabled]}>
              {num}
            </Text>
          </TouchableOpacity>
        ))}
        <TouchableOpacity
          style={[styles.numberButton, !biometricEnabled && styles.numberButtonDisabled]}
          onPress={attemptBiometricAuth}
          disabled={!biometricEnabled || isDisabled}
        >
          <Text style={styles.biometricText}>👆</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.numberButton, isDisabled && styles.numberButtonDisabled]}
          onPress={() => handleNumberPress('0')}
          disabled={isDisabled}
        >
          <Text style={[styles.numberText, isDisabled && styles.numberTextDisabled]}>
            0
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.numberButton, isDisabled && styles.numberButtonDisabled]}
          onPress={handleDelete}
          disabled={isDisabled}
        >
          <Text style={[styles.deleteText, isDisabled && styles.numberTextDisabled]}>
            ⌫
          </Text>
        </TouchableOpacity>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.icon}>🔒</Text>
        <Text style={styles.title}>FinCloud Locked</Text>
        <Text style={styles.subtitle}>Enter your PIN to unlock</Text>
        {error ? <Text style={styles.errorText}>{error}</Text> : null}
        {renderDots()}
      </View>
      {renderNumberPad()}
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
    fontSize: 64,
    marginBottom: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 16,
  },
  errorText: {
    fontSize: 14,
    color: '#FF3B30',
    marginTop: 8,
    textAlign: 'center',
    paddingHorizontal: 24,
  },
  dotsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 32,
  },
  dot: {
    width: 16,
    height: 16,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#007AFF',
    marginHorizontal: 8,
  },
  dotFilled: {
    backgroundColor: '#007AFF',
  },
  numberPad: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    paddingHorizontal: 24,
    paddingBottom: 48,
  },
  numberButton: {
    width: '30%',
    aspectRatio: 1,
    justifyContent: 'center',
    alignItems: 'center',
    margin: '1.5%',
  },
  numberButtonDisabled: {
    opacity: 0.3,
  },
  numberText: {
    fontSize: 32,
    fontWeight: '300',
    color: '#333',
  },
  numberTextDisabled: {
    color: '#999',
  },
  deleteText: {
    fontSize: 28,
    color: '#333',
  },
  biometricText: {
    fontSize: 28,
  },
});
