import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { StackNavigationProp } from '@react-navigation/stack';
import { MoreStackParamList } from '../../navigation/types';

type MoreScreenNavigationProp = StackNavigationProp<MoreStackParamList, 'MoreHome'>;

interface Props {
  navigation: MoreScreenNavigationProp;
}

export default function MoreScreen({ navigation }: Props) {
  const { t } = useTranslation();

  const menuItems = [
    {
      id: 'categories',
      icon: '🏷️',
      title: 'Categories',
      subtitle: 'Manage income and expense categories',
      onPress: () => navigation.navigate('Categories'),
    },
    {
      id: 'budgets',
      icon: '🎯',
      title: 'Budgets',
      subtitle: 'Set and track spending budgets',
      onPress: () => navigation.navigate('Budgets'),
    },
    {
      id: 'settings',
      icon: '⚙️',
      title: 'Settings',
      subtitle: 'App preferences and configuration',
      onPress: () => navigation.navigate('Settings'),
    },
    {
      id: 'security',
      icon: '🔒',
      title: 'Security',
      subtitle: 'PIN, biometric, and privacy settings',
      onPress: () => navigation.navigate('Security'),
    },
    {
      id: 'export',
      icon: '📤',
      title: 'Export Data',
      subtitle: 'Export your financial data as CSV',
      onPress: () => navigation.navigate('Export'),
    },
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>More</Text>
        <Text style={styles.headerSubtitle}>
          Manage your app settings and preferences
        </Text>
      </View>

      <View style={styles.menuList}>
        {menuItems.map((item, index) => (
          <TouchableOpacity
            key={item.id}
            style={[
              styles.menuItem,
              index === menuItems.length - 1 && styles.menuItemLast,
            ]}
            onPress={item.onPress}
          >
            <Text style={styles.menuIcon}>{item.icon}</Text>
            <View style={styles.menuContent}>
              <Text style={styles.menuTitle}>{item.title}</Text>
              <Text style={styles.menuSubtitle}>{item.subtitle}</Text>
            </View>
            <Text style={styles.menuChevron}>›</Text>
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>FinCloud v1.0.0</Text>
        <Text style={styles.footerSubtext}>Privacy-first personal finance</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    padding: 24,
    paddingTop: 16,
  },
  headerTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#666',
  },
  menuList: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    borderRadius: 12,
    overflow: 'hidden',
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  menuItemLast: {
    borderBottomWidth: 0,
  },
  menuIcon: {
    fontSize: 28,
    marginRight: 16,
  },
  menuContent: {
    flex: 1,
  },
  menuTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  menuSubtitle: {
    fontSize: 12,
    color: '#999',
  },
  menuChevron: {
    fontSize: 24,
    color: '#999',
  },
  footer: {
    alignItems: 'center',
    padding: 32,
  },
  footerText: {
    fontSize: 14,
    color: '#999',
    marginBottom: 4,
  },
  footerSubtext: {
    fontSize: 12,
    color: '#CCC',
  },
});
