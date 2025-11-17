import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Switch,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { StackNavigationProp } from '@react-navigation/stack';
import { MoreStackParamList } from '../../navigation/types';
import { mmkvStorage, StorageKeys } from '../../storage/mmkv';

type SettingsScreenNavigationProp = StackNavigationProp<
  MoreStackParamList,
  'Settings'
>;

interface Props {
  navigation: SettingsScreenNavigationProp;
}

const LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'ro', name: 'Romanian' },
];

const CURRENCIES = ['USD', 'EUR', 'GBP', 'RON', 'JPY', 'CAD', 'AUD'];

const THEMES = [
  { value: 'light', label: 'Light', icon: '☀️' },
  { value: 'dark', label: 'Dark', icon: '🌙' },
  { value: 'auto', label: 'Auto', icon: '🌗' },
];

export default function SettingsScreen({ navigation }: Props) {
  const { t } = useTranslation();
  const [language, setLanguage] = useState('en');
  const [currency, setCurrency] = useState('USD');
  const [theme, setTheme] = useState('light');
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [budgetAlerts, setBudgetAlerts] = useState(true);
  const [syncEnabled, setSyncEnabled] = useState(false);
  const [wifiOnly, setWifiOnly] = useState(true);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = () => {
    const lang = mmkvStorage.getString(StorageKeys.LANGUAGE) || 'en';
    const curr = mmkvStorage.getString(StorageKeys.CURRENCY) || 'USD';
    const thm = mmkvStorage.getString(StorageKeys.THEME) || 'light';

    setLanguage(lang);
    setCurrency(curr);
    setTheme(thm);

    const settings = mmkvStorage.getObject<any>(StorageKeys.APP_SETTINGS);
    if (settings) {
      setNotificationsEnabled(settings.notifications?.enabled ?? true);
      setBudgetAlerts(settings.notifications?.budgetAlerts ?? true);
      setSyncEnabled(settings.sync?.enabled ?? false);
      setWifiOnly(settings.sync?.wifiOnly ?? true);
    }
  };

  const saveSettings = () => {
    mmkvStorage.set(StorageKeys.LANGUAGE, language);
    mmkvStorage.set(StorageKeys.CURRENCY, currency);
    mmkvStorage.set(StorageKeys.THEME, theme);

    mmkvStorage.setObject(StorageKeys.APP_SETTINGS, {
      language,
      currency,
      theme,
      notifications: {
        enabled: notificationsEnabled,
        budgetAlerts,
        portfolioAlerts: true,
        transactionReminders: true,
      },
      sync: {
        enabled: syncEnabled,
        wifiOnly,
      },
    });

    Alert.alert('Success', 'Settings saved successfully');
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Appearance</Text>

        <View style={styles.setting}>
          <Text style={styles.settingLabel}>Language</Text>
          <View style={styles.languageButtons}>
            {LANGUAGES.map((lang) => (
              <TouchableOpacity
                key={lang.code}
                style={[
                  styles.optionButton,
                  language === lang.code && styles.optionButtonActive,
                ]}
                onPress={() => setLanguage(lang.code)}
              >
                <Text
                  style={[
                    styles.optionButtonText,
                    language === lang.code && styles.optionButtonTextActive,
                  ]}
                >
                  {lang.name}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={styles.setting}>
          <Text style={styles.settingLabel}>Theme</Text>
          <View style={styles.themeButtons}>
            {THEMES.map((thm) => (
              <TouchableOpacity
                key={thm.value}
                style={[
                  styles.optionButton,
                  theme === thm.value && styles.optionButtonActive,
                ]}
                onPress={() => setTheme(thm.value)}
              >
                <Text style={styles.themeIcon}>{thm.icon}</Text>
                <Text
                  style={[
                    styles.optionButtonText,
                    theme === thm.value && styles.optionButtonTextActive,
                  ]}
                >
                  {thm.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Currency</Text>
        <View style={styles.currencyGrid}>
          {CURRENCIES.map((curr) => (
            <TouchableOpacity
              key={curr}
              style={[
                styles.currencyButton,
                currency === curr && styles.currencyButtonActive,
              ]}
              onPress={() => setCurrency(curr)}
            >
              <Text
                style={[
                  styles.currencyButtonText,
                  currency === curr && styles.currencyButtonTextActive,
                ]}
              >
                {curr}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Notifications</Text>

        <View style={styles.switchSetting}>
          <Text style={styles.settingLabel}>Enable Notifications</Text>
          <Switch
            value={notificationsEnabled}
            onValueChange={setNotificationsEnabled}
            trackColor={{ false: '#E5E5EA', true: '#34C759' }}
            thumbColor="#fff"
          />
        </View>

        <View style={styles.switchSetting}>
          <Text style={styles.settingLabel}>Budget Alerts</Text>
          <Switch
            value={budgetAlerts}
            onValueChange={setBudgetAlerts}
            disabled={!notificationsEnabled}
            trackColor={{ false: '#E5E5EA', true: '#34C759' }}
            thumbColor="#fff"
          />
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Sync</Text>

        <View style={styles.switchSetting}>
          <Text style={styles.settingLabel}>Enable Cloud Sync</Text>
          <Switch
            value={syncEnabled}
            onValueChange={setSyncEnabled}
            trackColor={{ false: '#E5E5EA', true: '#34C759' }}
            thumbColor="#fff"
          />
        </View>

        <View style={styles.switchSetting}>
          <Text style={styles.settingLabel}>WiFi Only</Text>
          <Switch
            value={wifiOnly}
            onValueChange={setWifiOnly}
            disabled={!syncEnabled}
            trackColor={{ false: '#E5E5EA', true: '#34C759' }}
            thumbColor="#fff"
          />
        </View>
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
  setting: {
    marginBottom: 16,
  },
  settingLabel: {
    fontSize: 14,
    color: '#333',
    marginBottom: 8,
  },
  languageButtons: {
    flexDirection: 'row',
    marginHorizontal: -4,
  },
  themeButtons: {
    flexDirection: 'row',
    marginHorizontal: -4,
  },
  optionButton: {
    flex: 1,
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    padding: 12,
    margin: 4,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#E5E5EA',
  },
  optionButtonActive: {
    borderColor: '#007AFF',
    backgroundColor: '#E3F2FF',
  },
  optionButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  optionButtonTextActive: {
    color: '#007AFF',
  },
  themeIcon: {
    fontSize: 20,
    marginBottom: 4,
  },
  currencyGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -4,
  },
  currencyButton: {
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 16,
    margin: 4,
    borderWidth: 2,
    borderColor: '#E5E5EA',
  },
  currencyButtonActive: {
    borderColor: '#007AFF',
    backgroundColor: '#E3F2FF',
  },
  currencyButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  currencyButtonTextActive: {
    color: '#007AFF',
  },
  switchSetting: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
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
