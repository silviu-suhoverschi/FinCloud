import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Image,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { StackNavigationProp } from '@react-navigation/stack';
import { RouteProp } from '@react-navigation/native';
import { useFocusEffect } from '@react-navigation/native';
import { TransactionsStackParamList } from '../../navigation/types';
import { transactionRepository, accountRepository } from '../../repositories';
import Transaction from '../../models/Transaction';
import Account from '../../models/Account';

type TransactionDetailsScreenNavigationProp = StackNavigationProp<
  TransactionsStackParamList,
  'TransactionDetails'
>;
type TransactionDetailsScreenRouteProp = RouteProp<
  TransactionsStackParamList,
  'TransactionDetails'
>;

interface Props {
  navigation: TransactionDetailsScreenNavigationProp;
  route: TransactionDetailsScreenRouteProp;
}

export default function TransactionDetailsScreen({ navigation, route }: Props) {
  const { t } = useTranslation();
  const { transactionId } = route.params;
  const [transaction, setTransaction] = useState<Transaction | null>(null);
  const [account, setAccount] = useState<Account | null>(null);
  const [destinationAccount, setDestinationAccount] = useState<Account | null>(null);

  useFocusEffect(
    useCallback(() => {
      loadTransactionDetails();
    }, [transactionId])
  );

  const loadTransactionDetails = async () => {
    try {
      const txn = await transactionRepository.getById(transactionId);
      if (!txn) {
        Alert.alert('Error', 'Transaction not found');
        navigation.goBack();
        return;
      }

      setTransaction(txn);

      const acc = await accountRepository.getById(txn.accountId);
      setAccount(acc);

      if (txn.destinationAccountId) {
        const destAcc = await accountRepository.getById(txn.destinationAccountId);
        setDestinationAccount(destAcc);
      }
    } catch (error) {
      console.error('Error loading transaction details:', error);
      Alert.alert('Error', 'Failed to load transaction details');
    }
  };

  const handleEdit = () => {
    navigation.navigate('EditTransaction', { transactionId });
  };

  const handleDelete = () => {
    Alert.alert(
      'Delete Transaction',
      'Are you sure you want to delete this transaction?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await transactionRepository.delete(transactionId);
              Alert.alert('Success', 'Transaction deleted successfully');
              navigation.goBack();
            } catch (error) {
              console.error('Error deleting transaction:', error);
              Alert.alert('Error', 'Failed to delete transaction');
            }
          },
        },
      ]
    );
  };

  const formatCurrency = (amount: number, currency: string) => {
    return `${currency} ${amount.toFixed(2)}`;
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    });
  };

  if (!transaction) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading...</Text>
      </View>
    );
  }

  const typeColor =
    transaction.type === 'income'
      ? '#34C759'
      : transaction.type === 'expense'
      ? '#FF3B30'
      : '#007AFF';

  const typeIcon =
    transaction.type === 'income' ? '📈' : transaction.type === 'expense' ? '📉' : '🔄';

  return (
    <ScrollView style={styles.container}>
      {/* Amount Card */}
      <View style={[styles.amountCard, { backgroundColor: typeColor }]}>
        <Text style={styles.typeIcon}>{typeIcon}</Text>
        <Text style={styles.typeLabel}>
          {transaction.type.charAt(0).toUpperCase() + transaction.type.slice(1)}
        </Text>
        <Text style={styles.amount}>
          {transaction.type === 'income' ? '+' : transaction.type === 'expense' ? '-' : ''}
          {formatCurrency(transaction.amount, transaction.currency)}
        </Text>
      </View>

      {/* Details Section */}
      <View style={styles.section}>
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Description</Text>
          <Text style={styles.detailValue}>{transaction.description}</Text>
        </View>

        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Date</Text>
          <Text style={styles.detailValue}>{formatDate(transaction.date)}</Text>
        </View>

        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Account</Text>
          <Text style={styles.detailValue}>{account?.name || 'Unknown'}</Text>
        </View>

        {destinationAccount && (
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>To Account</Text>
            <Text style={styles.detailValue}>{destinationAccount.name}</Text>
          </View>
        )}

        {transaction.tags.length > 0 && (
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Tags</Text>
            <View style={styles.tagsContainer}>
              {transaction.tags.map((tag, index) => (
                <View key={index} style={styles.tag}>
                  <Text style={styles.tagText}>{tag}</Text>
                </View>
              ))}
            </View>
          </View>
        )}

        {transaction.recurring && (
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Recurring</Text>
            <Text style={styles.detailValue}>Yes</Text>
          </View>
        )}
      </View>

      {/* Attachments */}
      {transaction.attachments.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Attachments</Text>
          <View style={styles.attachmentsGrid}>
            {transaction.attachments.map((uri, index) => (
              <Image
                key={index}
                source={{ uri }}
                style={styles.attachmentImage}
                resizeMode="cover"
              />
            ))}
          </View>
        </View>
      )}

      {/* Action Buttons */}
      <View style={styles.actions}>
        <TouchableOpacity style={styles.actionButton} onPress={handleEdit}>
          <Text style={styles.actionButtonText}>Edit Transaction</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.actionButton, styles.deleteButton]}
          onPress={handleDelete}
        >
          <Text style={[styles.actionButtonText, styles.deleteButtonText]}>
            Delete Transaction
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
  },
  amountCard: {
    padding: 32,
    alignItems: 'center',
  },
  typeIcon: {
    fontSize: 48,
    marginBottom: 8,
  },
  typeLabel: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: 8,
  },
  amount: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#fff',
  },
  section: {
    backgroundColor: '#fff',
    margin: 16,
    padding: 16,
    borderRadius: 12,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  detailRow: {
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  detailLabel: {
    fontSize: 12,
    color: '#999',
    marginBottom: 4,
  },
  detailValue: {
    fontSize: 16,
    color: '#333',
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 4,
  },
  tag: {
    backgroundColor: '#E3F2FF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    marginRight: 8,
    marginTop: 4,
  },
  tagText: {
    fontSize: 12,
    color: '#007AFF',
    fontWeight: '600',
  },
  attachmentsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -4,
  },
  attachmentImage: {
    width: '31%',
    aspectRatio: 1,
    margin: '1%',
    borderRadius: 8,
    backgroundColor: '#F5F5F5',
  },
  actions: {
    padding: 16,
  },
  actionButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 12,
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  deleteButton: {
    backgroundColor: '#fff',
    borderWidth: 2,
    borderColor: '#FF3B30',
  },
  deleteButtonText: {
    color: '#FF3B30',
  },
});
