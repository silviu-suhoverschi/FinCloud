import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { MoreStackParamList } from './types';
import MoreScreen from '../screens/more/MoreScreen';
import CategoriesScreen from '../screens/more/CategoriesScreen';
import AddCategoryScreen from '../screens/more/AddCategoryScreen';
import EditCategoryScreen from '../screens/more/EditCategoryScreen';
import BudgetsScreen from '../screens/more/BudgetsScreen';
import AddBudgetScreen from '../screens/more/AddBudgetScreen';
import EditBudgetScreen from '../screens/more/EditBudgetScreen';
import SettingsScreen from '../screens/more/SettingsScreen';
import SecurityScreen from '../screens/more/SecurityScreen';
import ExportScreen from '../screens/more/ExportScreen';

const Stack = createStackNavigator<MoreStackParamList>();

export default function MoreNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: '#007AFF' },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: 'bold' },
      }}
    >
      <Stack.Screen
        name="MoreHome"
        component={MoreScreen}
        options={{ title: 'More' }}
      />
      <Stack.Screen
        name="Categories"
        component={CategoriesScreen}
        options={{ title: 'Categories' }}
      />
      <Stack.Screen
        name="AddCategory"
        component={AddCategoryScreen}
        options={{ title: 'Add Category' }}
      />
      <Stack.Screen
        name="EditCategory"
        component={EditCategoryScreen}
        options={{ title: 'Edit Category' }}
      />
      <Stack.Screen
        name="Budgets"
        component={BudgetsScreen}
        options={{ title: 'Budgets' }}
      />
      <Stack.Screen
        name="AddBudget"
        component={AddBudgetScreen}
        options={{ title: 'Add Budget' }}
      />
      <Stack.Screen
        name="EditBudget"
        component={EditBudgetScreen}
        options={{ title: 'Edit Budget' }}
      />
      <Stack.Screen
        name="Settings"
        component={SettingsScreen}
        options={{ title: 'Settings' }}
      />
      <Stack.Screen
        name="Security"
        component={SecurityScreen}
        options={{ title: 'Security' }}
      />
      <Stack.Screen
        name="Export"
        component={ExportScreen}
        options={{ title: 'Export Data' }}
      />
    </Stack.Navigator>
  );
}
