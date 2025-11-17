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
import { PortfolioStackParamList } from '../../navigation/types';
import { portfolioAssetRepository } from '../../repositories';
import { AssetType } from '../../types';

type AddAssetScreenNavigationProp = StackNavigationProp<
  PortfolioStackParamList,
  'AddAsset'
>;

interface Props {
  navigation: AddAssetScreenNavigationProp;
}

const USER_ID = 'offline-user';

const ASSET_TYPES: { value: AssetType; label: string; icon: string }[] = [
  { value: AssetType.STOCK, label: 'Stock', icon: '📈' },
  { value: AssetType.ETF, label: 'ETF', icon: '📊' },
  { value: AssetType.CRYPTO, label: 'Crypto', icon: '₿' },
  { value: AssetType.BOND, label: 'Bond', icon: '📜' },
  { value: AssetType.COMMODITY, label: 'Commodity', icon: '🏆' },
  { value: AssetType.REAL_ESTATE, label: 'Real Estate', icon: '🏠' },
];

export default function AddAssetScreen({ navigation }: Props) {
  const { t } = useTranslation();
  const [symbol, setSymbol] = useState('');
  const [name, setName] = useState('');
  const [type, setType] = useState<AssetType>(AssetType.STOCK);
  const [quantity, setQuantity] = useState('');
  const [price, setPrice] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    if (!symbol.trim()) {
      Alert.alert('Validation Error', 'Please enter a symbol');
      return;
    }

    if (!name.trim()) {
      Alert.alert('Validation Error', 'Please enter a name');
      return;
    }

    const quantityNum = parseFloat(quantity);
    if (isNaN(quantityNum) || quantityNum <= 0) {
      Alert.alert('Validation Error', 'Please enter a valid quantity');
      return;
    }

    const priceNum = parseFloat(price);
    if (isNaN(priceNum) || priceNum <= 0) {
      Alert.alert('Validation Error', 'Please enter a valid price');
      return;
    }

    try {
      setSaving(true);

      const totalCost = quantityNum * priceNum;
      const marketValue = quantityNum * priceNum;

      await portfolioAssetRepository.create({
        userId: USER_ID,
        symbol: symbol.trim().toUpperCase(),
        name: name.trim(),
        type,
        quantity: quantityNum,
        averageCost: priceNum,
        currentPrice: priceNum,
        currency: 'USD',
        marketValue,
        totalCost,
        gainLoss: 0,
        gainLossPercentage: 0,
      });

      Alert.alert('Success', 'Asset added successfully');
      navigation.goBack();
    } catch (error) {
      console.error('Error adding asset:', error);
      Alert.alert('Error', 'Failed to add asset');
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
        <View style={styles.section}>
          <Text style={styles.label}>Symbol *</Text>
          <TextInput
            style={styles.input}
            value={symbol}
            onChangeText={setSymbol}
            placeholder="e.g., AAPL, BTC, etc."
            placeholderTextColor="#999"
            autoCapitalize="characters"
          />
        </View>

        <View style={styles.section}>
          <Text style={styles.label}>Name *</Text>
          <TextInput
            style={styles.input}
            value={name}
            onChangeText={setName}
            placeholder="e.g., Apple Inc."
            placeholderTextColor="#999"
          />
        </View>

        <View style={styles.section}>
          <Text style={styles.label}>Asset Type *</Text>
          <View style={styles.typeGrid}>
            {ASSET_TYPES.map((item) => (
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

        <View style={styles.section}>
          <Text style={styles.label}>Quantity *</Text>
          <TextInput
            style={styles.input}
            value={quantity}
            onChangeText={setQuantity}
            placeholder="0"
            placeholderTextColor="#999"
            keyboardType="decimal-pad"
          />
        </View>

        <View style={styles.section}>
          <Text style={styles.label}>Purchase Price *</Text>
          <TextInput
            style={styles.input}
            value={price}
            onChangeText={setPrice}
            placeholder="0.00"
            placeholderTextColor="#999"
            keyboardType="decimal-pad"
          />
        </View>

        {quantity && price && (
          <View style={styles.totalCard}>
            <Text style={styles.totalLabel}>Total Cost</Text>
            <Text style={styles.totalAmount}>
              ${(parseFloat(quantity) * parseFloat(price) || 0).toFixed(2)}
            </Text>
          </View>
        )}
      </ScrollView>

      <View style={styles.footer}>
        <TouchableOpacity
          style={[styles.saveButton, saving && styles.saveButtonDisabled]}
          onPress={handleSave}
          disabled={saving}
        >
          <Text style={styles.saveButtonText}>
            {saving ? 'Adding...' : 'Add Asset'}
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
  typeGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -4,
  },
  typeButton: {
    width: '31%',
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 12,
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
    fontSize: 24,
    marginBottom: 8,
  },
  typeLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
    textAlign: 'center',
  },
  typeLabelActive: {
    color: '#007AFF',
  },
  totalCard: {
    backgroundColor: '#E3F2FF',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  totalLabel: {
    fontSize: 14,
    color: '#007AFF',
    marginBottom: 8,
  },
  totalAmount: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007AFF',
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
