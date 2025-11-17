import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { StackNavigationProp } from '@react-navigation/stack';
import { AccountsStackParamList } from '../../navigation/types';
import { accountRepository } from '../../repositories';
import { AccountType } from '../../types';

type AddAccountScreenNavigationProp = StackNavigationProp<
  AccountsStackParamList,
  'AddAccount'
>;

interface Props {
  navigation: AddAccountScreenNavigationProp;
}

const USER_ID = 'offline-user';
const MAX_FREE_ACCOUNTS = 5;

const ACCOUNT_TYPES: { value: AccountType; label: string; icon: string }[] = [
  { value: AccountType.BANK, label: 'Bank Account', icon: '🏦' },
  { value: AccountType.SAVINGS, label: 'Savings', icon: '💰' },
  { value: AccountType.CASH, label: 'Cash', icon: '💵' },
  { value: AccountType.CREDIT, label: 'Credit Card', icon: '💳' },
  { value: AccountType.INVESTMENT, label: 'Investment', icon: '📈' },
];

const CURRENCIES = ['USD', 'EUR', 'GBP', 'RON', 'JPY', 'CAD', 'AUD'];

export default function AddAccountScreen({ navigation }: Props) {
  const { t } = useTranslation();
  const [name, setName] = useState('');
  const [type, setType] = useState<AccountType>(AccountType.BANK);
  const [currency, setCurrency] = useState('USD');
  const [balance, setBalance] = useState('0');
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    // Validation
    if (!name.trim()) {
      Alert.alert('Validation Error', 'Please enter an account name');
      return;
    }

    const balanceNum = parseFloat(balance);
    if (isNaN(balanceNum)) {
      Alert.alert('Validation Error', 'Please enter a valid balance');
      return;
    }

    // Check FREE tier limit
    try {
      const existingAccounts = await accountRepository.getByUserId(USER_ID);
      if (existingAccounts.length >= MAX_FREE_ACCOUNTS) {
        Alert.alert(
          'Account Limit Reached',
          `You have reached the FREE tier limit of ${MAX_FREE_ACCOUNTS} accounts. Upgrade to Premium for unlimited accounts.`,
          [{ text: 'OK' }]
        );
        return;
      }

      setSaving(true);

      await accountRepository.create({
        userId: USER_ID,
        name: name.trim(),
        type,
        currency,
        balance: balanceNum,
        initialBalance: balanceNum,
        description: description.trim() || undefined,
        isActive: true,
      });

      Alert.alert('Success', 'Account created successfully');
      navigation.goBack();
    } catch (error) {
      console.error('Error creating account:', error);
      Alert.alert('Error', 'Failed to create account');
    } finally {
      setSaving(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.content}>
        {/* Account Name */}
        <View style={styles.section}>
          <Text style={styles.label}>Account Name *</Text>
          <TextInput
            style={styles.input}
            value={name}
            onChangeText={setName}
            placeholder="e.g., Main Checking"
            placeholderTextColor="#999"
          />
        </View>

        {/* Account Type */}
        <View style={styles.section}>
          <Text style={styles.label}>Account Type *</Text>
          <View style={styles.typeGrid}>
            {ACCOUNT_TYPES.map((item) => (
              <TouchableOpacity
                key={item.value}
                style={[
                  styles.typeButton,
                  type === item.value && styles.typeButtonActive,
                ]}
                onPress={() => setType(item.value)}
              >
                <Text style={styles.typeIcon}>{item.icon}</Text>
                <Text
                  style={[
                    styles.typeLabel,
                    type === item.value && styles.typeLabelActive,
                  ]}
                >
                  {item.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Currency */}
        <View style={styles.section}>
          <Text style={styles.label}>Currency *</Text>
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
                    styles.currencyText,
                    currency === curr && styles.currencyTextActive,
                  ]}
                >
                  {curr}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Initial Balance */}
        <View style={styles.section}>
          <Text style={styles.label}>Initial Balance *</Text>
          <TextInput
            style={styles.input}
            value={balance}
            onChangeText={setBalance}
            placeholder="0.00"
            placeholderTextColor="#999"
            keyboardType="decimal-pad"
          />
        </View>

        {/* Description */}
        <View style={styles.section}>
          <Text style={styles.label}>Description (Optional)</Text>
          <TextInput
            style={[styles.input, styles.textArea]}
            value={description}
            onChangeText={setDescription}
            placeholder="Add notes about this account..."
            placeholderTextColor="#999"
            multiline
            numberOfLines={3}
          />
        </View>

        {/* Info Box */}
        <View style={styles.infoBox}>
          <Text style={styles.infoIcon}>ℹ️</Text>
          <Text style={styles.infoText}>
            FREE tier includes up to {MAX_FREE_ACCOUNTS} accounts. Upgrade to Premium for unlimited accounts.
          </Text>
        </View>
      </ScrollView>

      {/* Save Button */}
      <View style={styles.footer}>
        <TouchableOpacity
          style={[styles.saveButton, saving && styles.saveButtonDisabled]}
          onPress={handleSave}
          disabled={saving}
        >
          <Text style={styles.saveButtonText}>
            {saving ? 'Creating...' : 'Create Account'}
          </Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  content: {
    padding: 16,
    paddingBottom: 100,
  },
  section: {
    marginBottom: 24,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    color: '#333',
    borderWidth: 1,
    borderColor: '#E5E5EA',
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  typeGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -4,
  },
  typeButton: {
    width: '48%',
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    margin: '1%',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#E5E5EA',
  },
  typeButtonActive: {
    borderColor: '#007AFF',
    backgroundColor: '#E3F2FF',
  },
  typeIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  typeLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    textAlign: 'center',
  },
  typeLabelActive: {
    color: '#007AFF',
  },
  currencyGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -4,
  },
  currencyButton: {
    backgroundColor: '#fff',
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
  currencyText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  currencyTextActive: {
    color: '#007AFF',
  },
  infoBox: {
    flexDirection: 'row',
    backgroundColor: '#E3F2FF',
    padding: 12,
    borderRadius: 8,
    marginTop: 8,
  },
  infoIcon: {
    fontSize: 16,
    marginRight: 8,
  },
  infoText: {
    flex: 1,
    fontSize: 12,
    color: '#007AFF',
    lineHeight: 18,
  },
  footer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    padding: 16,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#E5E5EA',
  },
  saveButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  saveButtonDisabled: {
    opacity: 0.5,
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
});
