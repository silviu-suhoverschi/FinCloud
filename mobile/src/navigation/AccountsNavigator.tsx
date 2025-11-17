import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { AccountsStackParamList } from './types';
import AccountsListScreen from '../screens/accounts/AccountsListScreen';
import AccountDetailsScreen from '../screens/accounts/AccountDetailsScreen';
import AddAccountScreen from '../screens/accounts/AddAccountScreen';
import EditAccountScreen from '../screens/accounts/EditAccountScreen';

const Stack = createStackNavigator<AccountsStackParamList>();

export default function AccountsNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: '#007AFF' },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: 'bold' },
      }}
    >
      <Stack.Screen
        name="AccountsList"
        component={AccountsListScreen}
        options={{ title: 'Accounts' }}
      />
      <Stack.Screen
        name="AccountDetails"
        component={AccountDetailsScreen}
        options={{ title: 'Account Details' }}
      />
      <Stack.Screen
        name="AddAccount"
        component={AddAccountScreen}
        options={{ title: 'Add Account' }}
      />
      <Stack.Screen
        name="EditAccount"
        component={EditAccountScreen}
        options={{ title: 'Edit Account' }}
      />
    </Stack.Navigator>
  );
}
