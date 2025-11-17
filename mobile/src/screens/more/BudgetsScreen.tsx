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
import { MoreStackParamList } from '../../navigation/types';
import { budgetRepository, categoryRepository } from '../../repositories';
import Budget from '../../models/Budget';

type BudgetsScreenNavigationProp = StackNavigationProp<
  MoreStackParamList,
  'Budgets'
>;

interface Props {
  navigation: BudgetsScreenNavigationProp;
}

const USER_ID = 'offline-user';

export default function BudgetsScreen({ navigation }: Props) {
  const { t } = useTranslation();
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  useFocusEffect(
    useCallback(() => {
      loadBudgets();
    }, [])
  );

  const loadBudgets = async () => {
    try {
      const data = await budgetRepository.getByUserId(USER_ID);
      setBudgets(data);
    } catch (error) {
      console.error('Error loading budgets:', error);
      Alert.alert('Error', 'Failed to load budgets');
    } finally {
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadBudgets();
  };

  const handleAddBudget = () => {
    navigation.navigate('AddBudget');
  };

  const handleBudgetPress = (budget: Budget) => {
    navigation.navigate('EditBudget', { budgetId: budget.id });
  };

  const getProgress = (budget: Budget) => {
    return budget.amount > 0 ? (budget.spent / budget.amount) * 100 : 0;
  };

  const formatCurrency = (amount: number) => {
    return `$${amount.toFixed(2)}`;
  };

  const renderBudget = ({ item }: { item: Budget }) => {
    const progress = getProgress(item);
    const isOverBudget = item.spent > item.amount;

    return (
      <TouchableOpacity
        style={styles.budgetCard}
        onPress={() => handleBudgetPress(item)}
      >
        <View style={styles.budgetHeader}>
          <Text style={styles.budgetName}>Budget #{item.id.slice(0, 8)}</Text>
          <Text style={styles.budgetPeriod}>
            {item.period.charAt(0).toUpperCase() + item.period.slice(1)}
          </Text>
        </View>

        <View style={styles.budgetAmounts}>
          <Text style={styles.budgetSpent}>
            {formatCurrency(item.spent)}
          </Text>
          <Text style={styles.budgetTotal}>
            of {formatCurrency(item.amount)}
          </Text>
        </View>

        <View style={styles.progressBarContainer}>
          <View
            style={[
              styles.progressBar,
              {
                width: `${Math.min(progress, 100)}%`,
                backgroundColor: isOverBudget ? '#FF3B30' : '#34C759',
              },
            ]}
          />
        </View>

        <Text
          style={[
            styles.budgetPercentage,
            isOverBudget && styles.budgetOverBudget,
          ]}
        >
          {progress.toFixed(0)}% {isOverBudget && '(Over Budget!)'}
        </Text>
      </TouchableOpacity>
    );
  };

  const renderEmpty = () => (
    <View style={styles.emptyState}>
      <Text style={styles.emptyStateIcon}>🎯</Text>
      <Text style={styles.emptyStateText}>No budgets yet</Text>
      <Text style={styles.emptyStateSubtext}>
        Set budgets to track your spending goals
      </Text>
      <TouchableOpacity style={styles.emptyStateButton} onPress={handleAddBudget}>
        <Text style={styles.emptyStateButtonText}>Add Budget</Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={budgets}
        renderItem={renderBudget}
        keyExtractor={(item) => item.id}
        ListEmptyComponent={renderEmpty}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        contentContainerStyle={styles.listContent}
      />

      <TouchableOpacity style={styles.fab} onPress={handleAddBudget}>
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
    padding: 16,
    paddingBottom: 80,
  },
  budgetCard: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  budgetHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  budgetName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  budgetPeriod: {
    fontSize: 12,
    color: '#666',
  },
  budgetAmounts: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginBottom: 8,
  },
  budgetSpent: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginRight: 8,
  },
  budgetTotal: {
    fontSize: 14,
    color: '#999',
  },
  progressBarContainer: {
    height: 8,
    backgroundColor: '#F0F0F0',
    borderRadius: 4,
    marginBottom: 8,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    borderRadius: 4,
  },
  budgetPercentage: {
    fontSize: 12,
    color: '#666',
  },
  budgetOverBudget: {
    color: '#FF3B30',
    fontWeight: '600',
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
