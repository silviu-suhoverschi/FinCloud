import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { PortfolioStackParamList } from './types';
import PortfolioScreen from '../screens/portfolio/PortfolioScreen';
import AssetDetailsScreen from '../screens/portfolio/AssetDetailsScreen';
import AddAssetScreen from '../screens/portfolio/AddAssetScreen';
import EditAssetScreen from '../screens/portfolio/EditAssetScreen';
import AddPortfolioTransactionScreen from '../screens/portfolio/AddPortfolioTransactionScreen';

const Stack = createStackNavigator<PortfolioStackParamList>();

export default function PortfolioNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: '#007AFF' },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: 'bold' },
      }}
    >
      <Stack.Screen
        name="PortfolioHome"
        component={PortfolioScreen}
        options={{ title: 'Portfolio' }}
      />
      <Stack.Screen
        name="AssetDetails"
        component={AssetDetailsScreen}
        options={{ title: 'Asset Details' }}
      />
      <Stack.Screen
        name="AddAsset"
        component={AddAssetScreen}
        options={{ title: 'Add Asset' }}
      />
      <Stack.Screen
        name="EditAsset"
        component={EditAssetScreen}
        options={{ title: 'Edit Asset' }}
      />
      <Stack.Screen
        name="AddPortfolioTransaction"
        component={AddPortfolioTransactionScreen}
        options={{ title: 'Add Transaction' }}
      />
    </Stack.Navigator>
  );
}
