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
import { PortfolioStackParamList } from '../../navigation/types';
import { portfolioAssetRepository } from '../../repositories';
import PortfolioAsset from '../../models/PortfolioAsset';

type PortfolioScreenNavigationProp = StackNavigationProp<
  PortfolioStackParamList,
  'PortfolioHome'
>;

interface Props {
  navigation: PortfolioScreenNavigationProp;
}

const USER_ID = 'offline-user';

export default function PortfolioScreen({ navigation }: Props) {
  const { t } = useTranslation();
  const [assets, setAssets] = useState<PortfolioAsset[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  useFocusEffect(
    useCallback(() => {
      loadPortfolio();
    }, [])
  );

  const loadPortfolio = async () => {
    try {
      setLoading(true);
      const data = await portfolioAssetRepository.getByUserId(USER_ID);
      setAssets(data);
    } catch (error) {
      console.error('Error loading portfolio:', error);
      Alert.alert('Error', 'Failed to load portfolio');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadPortfolio();
  };

  const handleAddAsset = () => {
    navigation.navigate('AddAsset');
  };

  const handleAssetPress = (asset: PortfolioAsset) => {
    navigation.navigate('AssetDetails', { assetId: asset.id });
  };

  const getTotalValue = () => {
    return assets.reduce((sum, asset) => sum + asset.marketValue, 0);
  };

  const getTotalGainLoss = () => {
    return assets.reduce((sum, asset) => sum + asset.gainLoss, 0);
  };

  const getTotalGainLossPercentage = () => {
    const totalCost = assets.reduce((sum, asset) => sum + asset.totalCost, 0);
    const gainLoss = getTotalGainLoss();
    return totalCost > 0 ? (gainLoss / totalCost) * 100 : 0;
  };

  const getAssetIcon = (type: string) => {
    switch (type) {
      case 'stock':
        return '📈';
      case 'etf':
        return '📊';
      case 'crypto':
        return '₿';
      case 'bond':
        return '📜';
      case 'commodity':
        return '🏆';
      default:
        return '💼';
    }
  };

  const formatCurrency = (amount: number) => {
    return `$${amount.toFixed(2)}`;
  };

  const renderAsset = ({ item }: { item: PortfolioAsset }) => (
    <TouchableOpacity
      style={styles.assetCard}
      onPress={() => handleAssetPress(item)}
    >
      <View style={styles.assetHeader}>
        <Text style={styles.assetIcon}>{getAssetIcon(item.type)}</Text>
        <View style={styles.assetInfo}>
          <Text style={styles.assetSymbol}>{item.symbol}</Text>
          <Text style={styles.assetName} numberOfLines={1}>
            {item.name}
          </Text>
        </View>
        <View style={styles.assetValues}>
          <Text style={styles.assetValue}>{formatCurrency(item.marketValue)}</Text>
          <Text
            style={[
              styles.assetGainLoss,
              item.gainLoss >= 0 ? styles.positiveGain : styles.negativeGain,
            ]}
          >
            {item.gainLoss >= 0 ? '+' : ''}
            {formatCurrency(item.gainLoss)} ({item.gainLossPercentage.toFixed(2)}%)
          </Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  const renderEmpty = () => (
    <View style={styles.emptyState}>
      <Text style={styles.emptyStateIcon}>📊</Text>
      <Text style={styles.emptyStateText}>No assets yet</Text>
      <Text style={styles.emptyStateSubtext}>
        Start building your investment portfolio
      </Text>
      <TouchableOpacity style={styles.emptyStateButton} onPress={handleAddAsset}>
        <Text style={styles.emptyStateButtonText}>Add Asset</Text>
      </TouchableOpacity>
    </View>
  );

  const renderHeader = () => {
    if (assets.length === 0) return null;

    const totalValue = getTotalValue();
    const totalGainLoss = getTotalGainLoss();
    const totalGainLossPercentage = getTotalGainLossPercentage();

    return (
      <View style={styles.header}>
        <Text style={styles.headerLabel}>Total Portfolio Value</Text>
        <Text style={styles.headerAmount}>{formatCurrency(totalValue)}</Text>
        <Text
          style={[
            styles.headerGainLoss,
            totalGainLoss >= 0 ? styles.positiveGain : styles.negativeGain,
          ]}
        >
          {totalGainLoss >= 0 ? '+' : ''}
          {formatCurrency(totalGainLoss)} ({totalGainLossPercentage.toFixed(2)}%)
        </Text>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <FlatList
        data={assets}
        renderItem={renderAsset}
        keyExtractor={(item) => item.id}
        ListHeaderComponent={renderHeader}
        ListEmptyComponent={!loading ? renderEmpty : null}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        contentContainerStyle={styles.listContent}
      />

      {/* Floating Action Button */}
      <TouchableOpacity style={styles.fab} onPress={handleAddAsset}>
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
  headerGainLoss: {
    fontSize: 16,
    fontWeight: '600',
  },
  positiveGain: {
    color: '#34C759',
  },
  negativeGain: {
    color: '#FF3B30',
  },
  assetCard: {
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
  assetHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  assetIcon: {
    fontSize: 32,
    marginRight: 12,
  },
  assetInfo: {
    flex: 1,
  },
  assetSymbol: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  assetName: {
    fontSize: 12,
    color: '#666',
  },
  assetValues: {
    alignItems: 'flex-end',
  },
  assetValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  assetGainLoss: {
    fontSize: 12,
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
