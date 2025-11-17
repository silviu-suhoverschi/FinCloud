import React, { useState, useEffect } from 'react';
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
import { RouteProp } from '@react-navigation/native';
import { TransactionsStackParamList } from '../../navigation/types';
import { transactionRepository, accountRepository } from '../../repositories';
import { TransactionType } from '../../types';
import DateTimePicker from '@react-native-community/datetimepicker';
import * as ImagePicker from 'expo-image-picker';

type AddTransactionScreenNavigationProp = StackNavigationProp<
  TransactionsStackParamList,
  'AddTransaction'
>;
type AddTransactionScreenRouteProp = RouteProp<TransactionsStackParamList, 'AddTransaction'>;

interface Props {
  navigation: AddTransactionScreenNavigationProp;
  route: AddTransactionScreenRouteProp;
}

const USER_ID = 'offline-user';

export default function AddTransactionScreen({ navigation, route }: Props) {
  const { t } = useTranslation();
  const { accountId, type: initialType } = route.params || {};

  const [type, setType] = useState<TransactionType>(initialType || TransactionType.EXPENSE);
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [date, setDate] = useState(new Date());
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [selectedAccountId, setSelectedAccountId] = useState(accountId || '');
  const [destinationAccountId, setDestinationAccountId] = useState('');
  const [accounts, setAccounts] = useState<any[]>([]);
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState('');
  const [attachments, setAttachments] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      const data = await accountRepository.getActive(USER_ID);
      setAccounts(data);
      if (!selectedAccountId && data.length > 0) {
        setSelectedAccountId(data[0].id);
      }
    } catch (error) {
      console.error('Error loading accounts:', error);
    }
  };

  const handlePickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission Required', 'Please allow access to photos');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsMultipleSelection: false,
      quality: 0.8,
    });

    if (!result.canceled && result.assets[0]) {
      setAttachments([...attachments, result.assets[0].uri]);
    }
  };

  const handleRemoveAttachment = (index: number) => {
    setAttachments(attachments.filter((_, i) => i !== index));
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags([...tags, tagInput.trim()]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tag: string) => {
    setTags(tags.filter((t) => t !== tag));
  };

  const handleSave = async () => {
    // Validation
    if (!description.trim()) {
      Alert.alert('Validation Error', 'Please enter a description');
      return;
    }

    const amountNum = parseFloat(amount);
    if (isNaN(amountNum) || amountNum <= 0) {
      Alert.alert('Validation Error', 'Please enter a valid amount');
      return;
    }

    if (!selectedAccountId) {
      Alert.alert('Validation Error', 'Please select an account');
      return;
    }

    if (type === TransactionType.TRANSFER && !destinationAccountId) {
      Alert.alert('Validation Error', 'Please select a destination account for transfer');
      return;
    }

    if (type === TransactionType.TRANSFER && selectedAccountId === destinationAccountId) {
      Alert.alert('Validation Error', 'Source and destination accounts must be different');
      return;
    }

    try {
      setSaving(true);

      const account = accounts.find((a) => a.id === selectedAccountId);
      if (!account) {
        throw new Error('Account not found');
      }

      await transactionRepository.create({
        userId: USER_ID,
        accountId: selectedAccountId,
        type,
        amount: amountNum,
        currency: account.currency,
        description: description.trim(),
        date,
        tags,
        recurring: false,
        attachments,
        destinationAccountId: type === TransactionType.TRANSFER ? destinationAccountId : undefined,
      });

      Alert.alert('Success', 'Transaction created successfully');
      navigation.goBack();
    } catch (error) {
      console.error('Error creating transaction:', error);
      Alert.alert('Error', 'Failed to create transaction');
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
        {/* Transaction Type */}
        <View style={styles.section}>
          <Text style={styles.label}>Type *</Text>
          <View style={styles.typeButtons}>
            <TouchableOpacity
              style={[
                styles.typeButton,
                type === TransactionType.EXPENSE && styles.typeButtonExpense,
              ]}
              onPress={() => setType(TransactionType.EXPENSE)}
            >
              <Text
                style={[
                  styles.typeButtonText,
                  type === TransactionType.EXPENSE && styles.typeButtonTextActive,
                ]}
              >
                📉 Expense
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.typeButton,
                type === TransactionType.INCOME && styles.typeButtonIncome,
              ]}
              onPress={() => setType(TransactionType.INCOME)}
            >
              <Text
                style={[
                  styles.typeButtonText,
                  type === TransactionType.INCOME && styles.typeButtonTextActive,
                ]}
              >
                📈 Income
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.typeButton,
                type === TransactionType.TRANSFER && styles.typeButtonTransfer,
              ]}
              onPress={() => setType(TransactionType.TRANSFER)}
            >
              <Text
                style={[
                  styles.typeButtonText,
                  type === TransactionType.TRANSFER && styles.typeButtonTextActive,
                ]}
              >
                🔄 Transfer
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Amount */}
        <View style={styles.section}>
          <Text style={styles.label}>Amount *</Text>
          <TextInput
            style={styles.input}
            value={amount}
            onChangeText={setAmount}
            placeholder="0.00"
            placeholderTextColor="#999"
            keyboardType="decimal-pad"
          />
        </View>

        {/* Description */}
        <View style={styles.section}>
          <Text style={styles.label}>Description *</Text>
          <TextInput
            style={styles.input}
            value={description}
            onChangeText={setDescription}
            placeholder="e.g., Groceries, Salary, etc."
            placeholderTextColor="#999"
          />
        </View>

        {/* Date */}
        <View style={styles.section}>
          <Text style={styles.label}>Date *</Text>
          <TouchableOpacity
            style={styles.input}
            onPress={() => setShowDatePicker(true)}
          >
            <Text style={styles.inputText}>
              {date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
              })}
            </Text>
          </TouchableOpacity>
          {showDatePicker && (
            <DateTimePicker
              value={date}
              mode="date"
              display="default"
              onChange={(event, selectedDate) => {
                setShowDatePicker(false);
                if (selectedDate) setDate(selectedDate);
              }}
            />
          )}
        </View>

        {/* Account */}
        <View style={styles.section}>
          <Text style={styles.label}>
            {type === TransactionType.TRANSFER ? 'From Account *' : 'Account *'}
          </Text>
          <View style={styles.accountsList}>
            {accounts.map((account) => (
              <TouchableOpacity
                key={account.id}
                style={[
                  styles.accountButton,
                  selectedAccountId === account.id && styles.accountButtonActive,
                ]}
                onPress={() => setSelectedAccountId(account.id)}
              >
                <Text
                  style={[
                    styles.accountButtonText,
                    selectedAccountId === account.id && styles.accountButtonTextActive,
                  ]}
                >
                  {account.name}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Destination Account (for transfers) */}
        {type === TransactionType.TRANSFER && (
          <View style={styles.section}>
            <Text style={styles.label}>To Account *</Text>
            <View style={styles.accountsList}>
              {accounts.map((account) => (
                <TouchableOpacity
                  key={account.id}
                  style={[
                    styles.accountButton,
                    destinationAccountId === account.id && styles.accountButtonActive,
                  ]}
                  onPress={() => setDestinationAccountId(account.id)}
                  disabled={account.id === selectedAccountId}
                >
                  <Text
                    style={[
                      styles.accountButtonText,
                      destinationAccountId === account.id && styles.accountButtonTextActive,
                      account.id === selectedAccountId && styles.accountButtonTextDisabled,
                    ]}
                  >
                    {account.name}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}

        {/* Tags */}
        <View style={styles.section}>
          <Text style={styles.label}>Tags (Optional)</Text>
          <View style={styles.tagInputContainer}>
            <TextInput
              style={[styles.input, styles.tagInput]}
              value={tagInput}
              onChangeText={setTagInput}
              placeholder="Add tag..."
              placeholderTextColor="#999"
              onSubmitEditing={handleAddTag}
            />
            <TouchableOpacity style={styles.addTagButton} onPress={handleAddTag}>
              <Text style={styles.addTagButtonText}>+</Text>
            </TouchableOpacity>
          </View>
          {tags.length > 0 && (
            <View style={styles.tagsContainer}>
              {tags.map((tag) => (
                <TouchableOpacity
                  key={tag}
                  style={styles.tag}
                  onPress={() => handleRemoveTag(tag)}
                >
                  <Text style={styles.tagText}>{tag}</Text>
                  <Text style={styles.tagRemove}>×</Text>
                </TouchableOpacity>
              ))}
            </View>
          )}
        </View>

        {/* Attachments */}
        <View style={styles.section}>
          <Text style={styles.label}>Attachments (Optional)</Text>
          <TouchableOpacity style={styles.addPhotoButton} onPress={handlePickImage}>
            <Text style={styles.addPhotoText}>📷 Add Photo</Text>
          </TouchableOpacity>
          {attachments.length > 0 && (
            <View style={styles.attachmentsContainer}>
              {attachments.map((uri, index) => (
                <View key={index} style={styles.attachmentPreview}>
                  <Text style={styles.attachmentText}>Photo {index + 1}</Text>
                  <TouchableOpacity onPress={() => handleRemoveAttachment(index)}>
                    <Text style={styles.attachmentRemove}>×</Text>
                  </TouchableOpacity>
                </View>
              ))}
            </View>
          )}
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
            {saving ? 'Creating...' : 'Create Transaction'}
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
  inputText: {
    fontSize: 16,
    color: '#333',
  },
  typeButtons: {
    flexDirection: 'row',
    marginHorizontal: -4,
  },
  typeButton: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 12,
    margin: 4,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#E5E5EA',
  },
  typeButtonExpense: {
    borderColor: '#FF3B30',
    backgroundColor: '#FFE5E5',
  },
  typeButtonIncome: {
    borderColor: '#34C759',
    backgroundColor: '#E5F9E5',
  },
  typeButtonTransfer: {
    borderColor: '#007AFF',
    backgroundColor: '#E3F2FF',
  },
  typeButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  typeButtonTextActive: {
    color: '#333',
  },
  accountsList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -4,
  },
  accountButton: {
    backgroundColor: '#fff',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 16,
    margin: 4,
    borderWidth: 2,
    borderColor: '#E5E5EA',
  },
  accountButtonActive: {
    borderColor: '#007AFF',
    backgroundColor: '#E3F2FF',
  },
  accountButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  accountButtonTextActive: {
    color: '#007AFF',
  },
  accountButtonTextDisabled: {
    color: '#CCC',
  },
  tagInputContainer: {
    flexDirection: 'row',
  },
  tagInput: {
    flex: 1,
    marginRight: 8,
  },
  addTagButton: {
    backgroundColor: '#007AFF',
    width: 48,
    height: 48,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  addTagButtonText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: '300',
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 8,
  },
  tag: {
    flexDirection: 'row',
    backgroundColor: '#E3F2FF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    marginRight: 8,
    marginTop: 4,
    alignItems: 'center',
  },
  tagText: {
    fontSize: 12,
    color: '#007AFF',
    fontWeight: '600',
    marginRight: 4,
  },
  tagRemove: {
    fontSize: 18,
    color: '#007AFF',
    fontWeight: '600',
  },
  addPhotoButton: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    borderWidth: 2,
    borderColor: '#E5E5EA',
    borderStyle: 'dashed',
    alignItems: 'center',
  },
  addPhotoText: {
    fontSize: 16,
    color: '#666',
  },
  attachmentsContainer: {
    marginTop: 8,
  },
  attachmentPreview: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    marginTop: 8,
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  attachmentText: {
    fontSize: 14,
    color: '#333',
  },
  attachmentRemove: {
    fontSize: 24,
    color: '#FF3B30',
    fontWeight: '600',
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
