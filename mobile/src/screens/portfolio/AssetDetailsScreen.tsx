import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Alert,
  RefreshControl,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { StackNavigationProp } from '@react-navigation/stack';
import { RouteProp } from '@react-navigation/native';
import { useFocusEffect } from '@react-navigation/native';
import { PortfolioStackParamList } from '../../navigation/types';
import { portfolioAssetRepository, portfolioTransactionRepository } from '../../repositories';
import PortfolioAsset from '../../models/PortfolioAsset';
import PortfolioTransaction from '../../models/PortfolioTransaction';

type AssetDetailsScreenNavigationProp = StackNavigationProp<
  PortfolioStackParamList,
  'AssetDetails'
>;
type AssetDetailsScreenRouteProp = RouteProp<PortfolioStackParamList, 'AssetDetails'>;

interface Props {
  navigation: AssetDetailsScreenNavigationProp;
  route: AssetDetailsScreenRouteProp;
}

export default function AssetDetailsScreen({ navigation, route }: Props) {
  const { t } = useTranslation();
  const { assetId } = route.params;
  const [asset, setAsset] = useState<PortfolioAsset | null>(null);
  const [transactions, setTransactions] = useState<PortfolioTransaction[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  useFocusEffect(
    useCallback(() => {
      loadAssetDetails();
    }, [assetId])
  );

  const loadAssetDetails = async () => {
    try {
      const assetData = await portfolioAssetRepository.getById(assetId);
      if (!assetData) {
        Alert.alert('Error', 'Asset not found');
        navigation.goBack();
        return;
      }

      setAsset(assetData);

      const txns = await portfolioTransactionRepository.getByAsset(assetId);
      setTransactions(txns);
    } catch (error) {
      console.error('Error loading asset details:', error);
      Alert.alert('Error', 'Failed to load asset details');
    } finally {
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadAssetDetails();
  };

  const handleEdit = () => {
    navigation.navigate('EditAsset', { assetId });
  };

  const handleDelete = () => {
    Alert.alert(
      'Delete Asset',
      'Are you sure you want to delete this asset? All associated transactions will also be deleted.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await portfolioAssetRepository.delete(assetId);
              Alert.alert('Success', 'Asset deleted successfully');
              navigation.goBack();
            } catch (error) {
              console.error('Error deleting asset:', error);
              Alert.alert('Error', 'Failed to delete asset');
            }
          },
        },
      ]
    );
  };

  const handleAddTransaction = () => {
    navigation.navigate('AddPortfolioTransaction', { assetId });
  };

  const formatCurrency = (amount: number) => {
    return `$${amount.toFixed(2)}`;
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const renderTransaction = ({ item }: { item: PortfolioTransaction }) => (
    <View style={styles.transactionItem}>
      <View style={styles.transactionInfo}>
        <Text style={styles.transactionIcon}>
          {item.type === 'buy' ? '📈' : item.type === 'sell' ? '📉' : '💰'}
        </Text>
        <View style={styles.transactionDetails}>
          <Text style={styles.transactionType}>
            {item.type.charAt(0).toUpperCase() + item.type.slice(1)}
          </Text>
          <Text style={styles.transactionDate}>{formatDate(item.date)}</Text>
        </View>
      </View>
      <View style={styles.transactionValues}>
        <Text style={styles.transactionQuantity}>
          {item.quantity} @ {formatCurrency(item.price)}
        </Text>
        <Text style={styles.transactionTotal}>{formatCurrency(item.total)}</Text>
      </View>
    </View>
  );

  const renderHeader = () => {
    if (!asset) return null;

    return (
      <View>
        <View style={styles.assetCard}>
          <Text style={styles.assetIcon}>
            {asset.type === 'stock' ? '📈' :
             asset.type === 'etf' ? '📊' :
             asset.type === 'crypto' ? '₿' :
             asset.type === 'bond' ? '📜' :
             asset.type === 'commodity' ? '🏆' : '💼'}
          </Text>
          <Text style={styles.assetSymbol}>{asset.symbol}</Text>
          <Text style={styles.assetName}>{asset.name}</Text>
          <Text style={styles.assetValue}>{formatCurrency(asset.marketValue)}</Text>
          <Text
            style={[
              styles.assetGainLoss,
              asset.gainLoss >= 0 ? styles.positiveGain : styles.negativeGain,
            ]}
          >
            {asset.gainLoss >= 0 ? '+' : ''}
            {formatCurrency(asset.gainLoss)} ({asset.gainLossPercentage.toFixed(2)}%)
          </Text>
        </View>

        <View style={styles.metricsGrid}>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Quantity</Text>
            <Text style={styles.metricValue}>{asset.quantity}</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Avg Cost</Text>
            <Text style={styles.metricValue}>{formatCurrency(asset.averageCost)}</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Current Price</Text>
            <Text style={styles.metricValue}>{formatCurrency(asset.currentPrice)}</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Total Cost</Text>
            <Text style={styles.metricValue}>{formatCurrency(asset.totalCost)}</Text>
          </View>
        </View>

        <View style={styles.actions}>
          <TouchableOpacity style={styles.actionButton} onPress={handleEdit}>
            <Text style={styles.actionButtonText}>Edit</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.actionButton, styles.deleteButton]}
            onPress={handleDelete}
          >
            <Text style={[styles.actionButtonText, styles.deleteButtonText]}>Delete</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Transactions</Text>
          <TouchableOpacity style={styles.addButton} onPress={handleAddTransaction}>
            <Text style={styles.addButtonText}>+ Add</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  };

  const renderEmpty = () => (
    <View style={styles.emptyState}>
      <Text style={styles.emptyStateIcon}>📝</Text>
      <Text style={styles.emptyStateText}>No transactions yet</Text>
      <TouchableOpacity style={styles.emptyStateButton} onPress={handleAddTransaction}>
        <Text style={styles.emptyStateButtonText}>Add Transaction</Text>
      </TouchableOpacity>
    </View>
  );

  if (!asset) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={transactions}
        renderItem={renderTransaction}
        keyExtractor={(item) => item.id}
        ListHeaderComponent={renderHeader}
        ListEmptyComponent={renderEmpty}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        contentContainerStyle={styles.listContent}
      />
    </View>
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
  listContent: {
    flexGrow: 1,
  },
  assetCard: {
    backgroundColor: '#007AFF',
    margin: 16,
    padding: 24,
    borderRadius: 16,
    alignItems: 'center',
  },
  assetIcon: {
    fontSize: 48,
    marginBottom: 12,
  },
  assetSymbol: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 4,
  },
  assetName: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: 16,
    textAlign: 'center',
  },
  assetValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 4,
  },
  assetGainLoss: {
    fontSize: 16,
    fontWeight: '600',
  },
  positiveGain: {
    color: '#34C759',
  },
  negativeGain: {
    color: '#FF3B30',
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 16,
    marginBottom: 16,
  },
  metricCard: {
    width: '48%',
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    margin: '1%',
  },
  metricLabel: {
    fontSize: 12,
    color: '#999',
    marginBottom: 4,
  },
  metricValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  actions: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    marginBottom: 16,
  },
  actionButton: {
    flex: 1,
    backgroundColor: '#fff',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 4,
  },
  actionButtonText: {
    color: '#007AFF',
    fontSize: 16,
    fontWeight: '600',
  },
  deleteButton: {
    backgroundColor: '#fff',
  },
  deleteButtonText: {
    color: '#FF3B30',
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  addButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  addButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  transactionItem: {
    backgroundColor: '#fff',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 8,
    borderRadius: 8,
  },
  transactionInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  transactionIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  transactionDetails: {
    flex: 1,
  },
  transactionType: {
    fontSize: 16,
    color: '#333',
    marginBottom: 4,
  },
  transactionDate: {
    fontSize: 12,
    color: '#999',
  },
  transactionValues: {
    alignItems: 'flex-end',
  },
  transactionQuantity: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  transactionTotal: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  emptyState: {
    padding: 48,
    alignItems: 'center',
  },
  emptyStateIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyStateText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 16,
    textAlign: 'center',
  },
  emptyStateButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  emptyStateButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
