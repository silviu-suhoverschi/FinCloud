import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { BottomTabsParamList } from './types';
import DashboardNavigator from './DashboardNavigator';
import AccountsNavigator from './AccountsNavigator';
import TransactionsNavigator from './TransactionsNavigator';
import PortfolioNavigator from './PortfolioNavigator';
import MoreNavigator from './MoreNavigator';
import { Text, View } from 'react-native';
import { useTranslation } from 'react-i18next';

const Tab = createBottomTabNavigator<BottomTabsParamList>();

// Simple icon component (will be replaced with actual icons later)
const TabIcon = ({ name, focused }: { name: string; focused: boolean }) => (
  <View style={{ alignItems: 'center', justifyContent: 'center' }}>
    <Text style={{ fontSize: 24, color: focused ? '#007AFF' : '#999' }}>{name}</Text>
  </View>
);

export default function MainNavigator() {
  const { t } = useTranslation();

  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: '#999',
        tabBarStyle: {
          backgroundColor: '#fff',
          borderTopWidth: 1,
          borderTopColor: '#E5E5E5',
        },
      }}
    >
      <Tab.Screen
        name="Dashboard"
        component={DashboardNavigator}
        options={{
          tabBarLabel: t('navigation.dashboard'),
          tabBarIcon: ({ focused }) => <TabIcon name="📊" focused={focused} />,
        }}
      />
      <Tab.Screen
        name="Accounts"
        component={AccountsNavigator}
        options={{
          tabBarLabel: t('navigation.accounts'),
          tabBarIcon: ({ focused }) => <TabIcon name="💳" focused={focused} />,
        }}
      />
      <Tab.Screen
        name="Transactions"
        component={TransactionsNavigator}
        options={{
          tabBarLabel: t('navigation.transactions'),
          tabBarIcon: ({ focused }) => <TabIcon name="💸" focused={focused} />,
        }}
      />
      <Tab.Screen
        name="Portfolio"
        component={PortfolioNavigator}
        options={{
          tabBarLabel: t('navigation.portfolio'),
          tabBarIcon: ({ focused }) => <TabIcon name="📈" focused={focused} />,
        }}
      />
      <Tab.Screen
        name="More"
        component={MoreNavigator}
        options={{
          tabBarLabel: t('navigation.more'),
          tabBarIcon: ({ focused }) => <TabIcon name="⚙️" focused={focused} />,
        }}
      />
    </Tab.Navigator>
  );
}
