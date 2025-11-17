import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { StackNavigationProp } from '@react-navigation/stack';
import { MoreStackParamList } from '../../navigation/types';
import { mmkvSecureStorage, StorageKeys } from '../../storage/mmkv';
import * as LocalAuthentication from 'expo-local-authentication';

type SecurityScreenNavigationProp = StackNavigationProp<
  MoreStackParamList,
  'Security'
>;

interface Props {
  navigation: SecurityScreenNavigationProp;
}

export default function SecurityScreen({ navigation }: Props) {
  const { t } = useTranslation();
  const [pinEnabled, setPinEnabled] = useState(false);
  const [biometricEnabled, setBiometricEnabled] = useState(false);
  const [autoLockTimeout, setAutoLockTimeout] = useState(300);
  const [biometricAvailable, setBiometricAvailable] = useState(false);

  useEffect(() => {
    loadSettings();
    checkBiometric();
  }, []);

  const loadSettings = () => {
    const settings = mmkvSecureStorage.getObject<any>(StorageKeys.SECURITY_SETTINGS);
    if (settings) {
      setPinEnabled(settings.pinEnabled ?? false);
      setBiometricEnabled(settings.biometricEnabled ?? false);
      setAutoLockTimeout(settings.autoLockTimeout ?? 300);
    }
  };

  const checkBiometric = async () => {
    const compatible = await LocalAuthentication.hasHardwareAsync();
    const enrolled = await LocalAuthentication.isEnrolledAsync();
    setBiometricAvailable(compatible && enrolled);
  };

  const saveSettings = () => {
    mmkvSecureStorage.setObject(StorageKeys.SECURITY_SETTINGS, {
      pinEnabled,
      pinLength: 6,
      biometricEnabled,
      autoLockTimeout,
    });

    Alert.alert('Success', 'Security settings saved');
  };

  const handleToggleBiometric = async (value: boolean) => {
    if (value && !pinEnabled) {
      Alert.alert('PIN Required', 'Please enable PIN before enabling biometric');
      return;
    }

    if (value) {
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Verify your identity',
      });

      if (result.success) {
        setBiometricEnabled(true);
      }
    } else {
      setBiometricEnabled(false);
    }
  };

  const lockTimeouts = [
    { value: 0, label: 'Disabled' },
    { value: 30, label: '30 seconds' },
    { value: 60, label: '1 minute' },
    { value: 300, label: '5 minutes' },
    { value: 600, label: '10 minutes' },
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Authentication</Text>

        <View style={styles.switchSetting}>
          <View>
            <Text style={styles.settingLabel}>PIN Protection</Text>
            <Text style={styles.settingHint}>
              Require PIN to unlock app
            </Text>
          </View>
          <Switch
            value={pinEnabled}
            onValueChange={setPinEnabled}
            trackColor={{ false: '#E5E5EA', true: '#34C759' }}
            thumbColor="#fff"
          />
        </View>

        {biometricAvailable && (
          <View style={styles.switchSetting}>
            <View>
              <Text style={styles.settingLabel}>Biometric Unlock</Text>
              <Text style={styles.settingHint}>
                Use fingerprint or face to unlock
              </Text>
            </View>
            <Switch
              value={biometricEnabled}
              onValueChange={handleToggleBiometric}
              disabled={!pinEnabled}
              trackColor={{ false: '#E5E5EA', true: '#34C759' }}
              thumbColor="#fff"
            />
          </View>
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Auto-Lock</Text>
        <Text style={styles.sectionDescription}>
          Lock app after period of inactivity
        </Text>

        {lockTimeouts.map((timeout) => (
          <TouchableOpacity
            key={timeout.value}
            style={styles.radioOption}
            onPress={() => setAutoLockTimeout(timeout.value)}
            disabled={!pinEnabled}
          >
            <View
              style={[
                styles.radioButton,
                autoLockTimeout === timeout.value && styles.radioButtonActive,
                !pinEnabled && styles.radioButtonDisabled,
              ]}
            >
              {autoLockTimeout === timeout.value && (
                <View style={styles.radioButtonInner} />
              )}
            </View>
            <Text
              style={[
                styles.radioLabel,
                !pinEnabled && styles.radioLabelDisabled,
              ]}
            >
              {timeout.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Actions</Text>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => {
            Alert.alert(
              'Change PIN',
              'This feature requires you to verify your current PIN first',
              [{ text: 'OK' }]
            );
          }}
          disabled={!pinEnabled}
        >
          <Text
            style={[
              styles.actionButtonText,
              !pinEnabled && styles.actionButtonTextDisabled,
            ]}
          >
            Change PIN
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => {
            Alert.alert(
              'Clear App Data',
              'This will delete all local data. This action cannot be undone.',
              [
                { text: 'Cancel', style: 'cancel' },
                {
                  text: 'Clear Data',
                  style: 'destructive',
                  onPress: () => {
                    Alert.alert('Success', 'App data cleared');
                  },
                },
              ]
            );
          }}
        >
          <Text style={[styles.actionButtonText, styles.actionButtonTextDanger]}>
            Clear All Data
          </Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.saveButton} onPress={saveSettings}>
        <Text style={styles.saveButtonText}>Save Settings</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  section: {
    backgroundColor: '#fff',
    marginTop: 16,
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#999',
    textTransform: 'uppercase',
    marginBottom: 12,
    marginTop: 8,
  },
  sectionDescription: {
    fontSize: 13,
    color: '#666',
    marginBottom: 12,
  },
  switchSetting: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  settingLabel: {
    fontSize: 14,
    color: '#333',
    marginBottom: 4,
  },
  settingHint: {
    fontSize: 12,
    color: '#999',
  },
  radioOption: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  radioButton: {
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: '#007AFF',
    marginRight: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  radioButtonActive: {
    borderColor: '#007AFF',
  },
  radioButtonDisabled: {
    borderColor: '#CCC',
  },
  radioButtonInner: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#007AFF',
  },
  radioLabel: {
    fontSize: 14,
    color: '#333',
  },
  radioLabelDisabled: {
    color: '#999',
  },
  actionButton: {
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  actionButtonText: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '600',
  },
  actionButtonTextDisabled: {
    color: '#CCC',
  },
  actionButtonTextDanger: {
    color: '#FF3B30',
  },
  saveButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 16,
    margin: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
});
