import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { StackNavigationProp } from '@react-navigation/stack';
import { useFocusEffect } from '@react-navigation/native';
import { AccountsStackParamList } from '../../navigation/types';
import { accountRepository } from '../../repositories';
import Account from '../../models/Account';

type AccountsListScreenNavigationProp = StackNavigationProp<
  AccountsStackParamList,
  'AccountsList'
>;

interface Props {
  navigation: AccountsListScreenNavigationProp;
}

const USER_ID = 'offline-user';

export default function AccountsListScreen({ navigation }: Props) {
  const { t } = useTranslation();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  useFocusEffect(
    useCallback(() => {
      loadAccounts();
    }, [])
  );

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const data = await accountRepository.getByUserId(USER_ID);
      setAccounts(data);
    } catch (error) {
      console.error('Error loading accounts:', error);
      Alert.alert('Error', 'Failed to load accounts');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadAccounts();
  };

  const handleAddAccount = () => {
    navigation.navigate('AddAccount');
  };

  const handleAccountPress = (account: Account) => {
    navigation.navigate('AccountDetails', { accountId: account.id });
  };

  const getAccountIcon = (type: string) => {
    switch (type) {
      case 'bank':
        return '🏦';
      case 'savings':
        return '💰';
      case 'cash':
        return '💵';
      case 'credit':
        return '💳';
      case 'investment':
        return '📈';
      default:
        return '💼';
    }
  };

  const formatCurrency = (amount: number, currency: string) => {
    return `${currency} ${amount.toFixed(2)}`;
  };

  const renderAccount = ({ item }: { item: Account }) => (
    <TouchableOpacity
      style={styles.accountCard}
      onPress={() => handleAccountPress(item)}
    >
      <View style={styles.accountHeader}>
        <Text style={styles.accountIcon}>{getAccountIcon(item.type)}</Text>
        <View style={styles.accountInfo}>
          <Text style={styles.accountName}>{item.name}</Text>
          <Text style={styles.accountType}>
            {item.type.charAt(0).toUpperCase() + item.type.slice(1)}
          </Text>
        </View>
        <View style={styles.accountBalance}>
          <Text style={[styles.balanceAmount, item.balance < 0 && styles.negativeBalance]}>
            {formatCurrency(item.balance, item.currency)}
          </Text>
          {!item.isActive && (
            <Text style={styles.inactiveLabel}>Inactive</Text>
          )}
        </View>
      </View>
    </TouchableOpacity>
  );

  const renderEmpty = () => (
    <View style={styles.emptyState}>
      <Text style={styles.emptyStateIcon}>🏦</Text>
      <Text style={styles.emptyStateText}>No accounts yet</Text>
      <Text style={styles.emptyStateSubtext}>
        Create your first account to start tracking your finances
      </Text>
      <TouchableOpacity style={styles.emptyStateButton} onPress={handleAddAccount}>
        <Text style={styles.emptyStateButtonText}>Add Account</Text>
      </TouchableOpacity>
    </View>
  );

  const renderHeader = () => {
    const totalBalance = accounts.reduce((sum, acc) => {
      if (acc.isActive) {
        // Simple sum for now (would need currency conversion in real app)
        return sum + acc.balance;
      }
      return sum;
    }, 0);

    return (
      <View style={styles.header}>
        <Text style={styles.headerLabel}>Total Balance</Text>
        <Text style={styles.headerAmount}>${totalBalance.toFixed(2)}</Text>
        <Text style={styles.headerSubtext}>{accounts.length} accounts</Text>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <FlatList
        data={accounts}
        renderItem={renderAccount}
        keyExtractor={(item) => item.id}
        ListHeaderComponent={accounts.length > 0 ? renderHeader : null}
        ListEmptyComponent={!loading ? renderEmpty : null}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        contentContainerStyle={styles.listContent}
      />

      {/* Floating Action Button */}
      <TouchableOpacity style={styles.fab} onPress={handleAddAccount}>
        <Text style={styles.fabText}>+</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  listContent: {
    flexGrow: 1,
    paddingBottom: 80,
  },
  header: {
    backgroundColor: '#007AFF',
    padding: 24,
    margin: 16,
    borderRadius: 16,
    alignItems: 'center',
  },
  headerLabel: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: 8,
  },
  headerAmount: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 4,
  },
  headerSubtext: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.7)',
  },
  accountCard: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginBottom: 12,
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  accountHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  accountIcon: {
    fontSize: 32,
    marginRight: 12,
  },
  accountInfo: {
    flex: 1,
  },
  accountName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  accountType: {
    fontSize: 12,
    color: '#666',
  },
  accountBalance: {
    alignItems: 'flex-end',
  },
  balanceAmount: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  negativeBalance: {
    color: '#FF3B30',
  },
  inactiveLabel: {
    fontSize: 10,
    color: '#FF3B30',
    marginTop: 4,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 48,
  },
  emptyStateIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  emptyStateText: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
    textAlign: 'center',
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 24,
  },
  emptyStateButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 32,
    paddingVertical: 12,
    borderRadius: 8,
  },
  emptyStateButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  fab: {
    position: 'absolute',
    right: 16,
    bottom: 16,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 8,
  },
  fabText: {
    color: '#fff',
    fontSize: 32,
    fontWeight: '300',
  },
});
