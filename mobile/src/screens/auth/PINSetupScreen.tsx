import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Vibration,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { StackNavigationProp } from '@react-navigation/stack';
import { RouteProp } from '@react-navigation/native';
import { AuthStackParamList } from '../../navigation/types';
import { mmkvSecureStorage, StorageKeys } from '../../storage/mmkv';
import * as Crypto from 'expo-crypto';

type PINSetupScreenNavigationProp = StackNavigationProp<AuthStackParamList, 'PINSetup'>;
type PINSetupScreenRouteProp = RouteProp<AuthStackParamList, 'PINSetup'>;

interface Props {
  navigation: PINSetupScreenNavigationProp;
  route: PINSetupScreenRouteProp;
}

const PIN_LENGTHS = [4, 6, 8] as const;

export default function PINSetupScreen({ navigation, route }: Props) {
  const { t } = useTranslation();
  const { mode } = route.params;

  const [selectedLength, setSelectedLength] = useState<4 | 6 | 8>(6);
  const [pin, setPin] = useState('');
  const [confirmPin, setConfirmPin] = useState('');
  const [step, setStep] = useState<'length' | 'create' | 'confirm' | 'verify'>(
    mode === 'create' ? 'length' : 'verify'
  );
  const [error, setError] = useState('');

  useEffect(() => {
    if (mode === 'verify') {
      setStep('verify');
      const settings = mmkvSecureStorage.getObject<any>(StorageKeys.SECURITY_SETTINGS);
      if (settings?.pinLength) {
        setSelectedLength(settings.pinLength);
      }
    }
  }, [mode]);

  const handleNumberPress = (num: string) => {
    setError('');

    if (step === 'length') return;

    const currentPin = step === 'confirm' ? confirmPin : pin;
    const maxLength = selectedLength;

    if (currentPin.length < maxLength) {
      const newPin = currentPin + num;

      if (step === 'create') {
        setPin(newPin);
        if (newPin.length === maxLength) {
          setTimeout(() => setStep('confirm'), 300);
        }
      } else if (step === 'confirm') {
        setConfirmPin(newPin);
        if (newPin.length === maxLength) {
          setTimeout(() => handleConfirmComplete(newPin), 300);
        }
      } else if (step === 'verify') {
        setPin(newPin);
        if (newPin.length === maxLength) {
          setTimeout(() => handleVerify(newPin), 300);
        }
      }
    }
  };

  const handleDelete = () => {
    setError('');

    if (step === 'confirm') {
      setConfirmPin(confirmPin.slice(0, -1));
    } else {
      setPin(pin.slice(0, -1));
    }
  };

  const handleConfirmComplete = async (newPin: string) => {
    if (newPin === pin) {
      // Hash the PIN before storing
      const pinHash = await Crypto.digestStringAsync(
        Crypto.CryptoDigestAlgorithm.SHA256,
        pin
      );

      mmkvSecureStorage.set(StorageKeys.PIN_HASH, pinHash);
      mmkvSecureStorage.setObject(StorageKeys.SECURITY_SETTINGS, {
        pinEnabled: true,
        pinLength: selectedLength,
        biometricEnabled: false,
        autoLockTimeout: 300, // 5 minutes default
      });

      navigation.navigate('BiometricSetup');
    } else {
      setError('PINs do not match. Please try again.');
      Vibration.vibrate(500);
      setPin('');
      setConfirmPin('');
      setStep('create');
    }
  };

  const handleVerify = async (enteredPin: string) => {
    const storedPinHash = mmkvSecureStorage.get(StorageKeys.PIN_HASH);
    const enteredPinHash = await Crypto.digestStringAsync(
      Crypto.CryptoDigestAlgorithm.SHA256,
      enteredPin
    );

    if (enteredPinHash === storedPinHash) {
      // PIN verified successfully
      mmkvSecureStorage.set(StorageKeys.LAST_ACTIVITY, Date.now().toString());
      // Navigate to main app (this would be handled by the root navigator)
      Alert.alert('Success', 'PIN verified successfully');
      setPin('');
    } else {
      setError('Incorrect PIN. Please try again.');
      Vibration.vibrate(500);
      setPin('');
    }
  };

  const renderDots = () => {
    const currentPin = step === 'confirm' ? confirmPin : pin;
    const dots = [];

    for (let i = 0; i < selectedLength; i++) {
      dots.push(
        <View
          key={i}
          style={[
            styles.dot,
            i < currentPin.length && styles.dotFilled,
          ]}
        />
      );
    }

    return <View style={styles.dotsContainer}>{dots}</View>;
  };

  const renderTitle = () => {
    if (step === 'length') return 'Choose PIN Length';
    if (step === 'create') return 'Create Your PIN';
    if (step === 'confirm') return 'Confirm Your PIN';
    return 'Enter Your PIN';
  };

  const renderNumberPad = () => {
    return (
      <View style={styles.numberPad}>
        {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((num) => (
          <TouchableOpacity
            key={num}
            style={styles.numberButton}
            onPress={() => handleNumberPress(num.toString())}
          >
            <Text style={styles.numberText}>{num}</Text>
          </TouchableOpacity>
        ))}
        <View style={styles.numberButton} />
        <TouchableOpacity
          style={styles.numberButton}
          onPress={() => handleNumberPress('0')}
        >
          <Text style={styles.numberText}>0</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.numberButton}
          onPress={handleDelete}
        >
          <Text style={styles.deleteText}>⌫</Text>
        </TouchableOpacity>
      </View>
    );
  };

  if (step === 'length') {
    return (
      <View style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.title}>{renderTitle()}</Text>
          <Text style={styles.subtitle}>
            Select how many digits you want for your PIN
          </Text>

          <View style={styles.lengthOptions}>
            {PIN_LENGTHS.map((length) => (
              <TouchableOpacity
                key={length}
                style={[
                  styles.lengthButton,
                  selectedLength === length && styles.lengthButtonActive,
                ]}
                onPress={() => setSelectedLength(length)}
              >
                <Text
                  style={[
                    styles.lengthButtonText,
                    selectedLength === length && styles.lengthButtonTextActive,
                  ]}
                >
                  {length} digits
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <TouchableOpacity
            style={styles.continueButton}
            onPress={() => setStep('create')}
          >
            <Text style={styles.continueButtonText}>Continue</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>{renderTitle()}</Text>
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
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 32,
  },
  errorText: {
    fontSize: 14,
    color: '#FF3B30',
    marginTop: 8,
    textAlign: 'center',
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
  lengthOptions: {
    width: '100%',
    marginBottom: 32,
  },
  lengthButton: {
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#E5E5EA',
    marginBottom: 12,
    alignItems: 'center',
  },
  lengthButtonActive: {
    borderColor: '#007AFF',
    backgroundColor: '#E3F2FF',
  },
  lengthButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666',
  },
  lengthButtonTextActive: {
    color: '#007AFF',
  },
  continueButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 16,
    paddingHorizontal: 48,
    borderRadius: 12,
    width: '100%',
    alignItems: 'center',
  },
  continueButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
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
  numberText: {
    fontSize: 32,
    fontWeight: '300',
    color: '#333',
  },
  deleteText: {
    fontSize: 28,
    color: '#333',
  },
});
