import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { StackNavigationProp } from '@react-navigation/stack';
import { MoreStackParamList } from '../../navigation/types';
import { transactionRepository, accountRepository } from '../../repositories';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';

type ExportScreenNavigationProp = StackNavigationProp<
  MoreStackParamList,
  'Export'
>;

interface Props {
  navigation: ExportScreenNavigationProp;
}

const USER_ID = 'offline-user';

export default function ExportScreen({ navigation }: Props) {
  const { t } = useTranslation();
  const [exporting, setExporting] = useState(false);

  const exportTransactionsCSV = async () => {
    try {
      setExporting(true);

      const transactions = await transactionRepository.getByUserId(USER_ID);

      if (transactions.length === 0) {
        Alert.alert('No Data', 'No transactions to export');
        return;
      }

      // Create CSV content
      const headers = 'Date,Type,Description,Amount,Currency,Account,Category\n';
      const rows = transactions.map((t) => {
        const date = t.date.toISOString().split('T')[0];
        return `${date},${t.type},${t.description},${t.amount},${t.currency},${t.accountId},${t.categoryId || ''}`;
      }).join('\n');

      const csv = headers + rows;

      // Save to file
      const fileName = `fincloud_transactions_${new Date().toISOString().split('T')[0]}.csv`;
      const fileUri = FileSystem.documentDirectory + fileName;

      await FileSystem.writeAsStringAsync(fileUri, csv);

      // Share file
      if (await Sharing.isAvailableAsync()) {
        await Sharing.shareAsync(fileUri);
        Alert.alert('Success', 'Transactions exported successfully');
      } else {
        Alert.alert('Success', `File saved to ${fileUri}`);
      }
    } catch (error) {
      console.error('Error exporting transactions:', error);
      Alert.alert('Error', 'Failed to export transactions');
    } finally {
      setExporting(false);
    }
  };

  const exportAccountsCSV = async () => {
    try {
      setExporting(true);

      const accounts = await accountRepository.getByUserId(USER_ID);

      if (accounts.length === 0) {
        Alert.alert('No Data', 'No accounts to export');
        return;
      }

      // Create CSV content
      const headers = 'Name,Type,Currency,Balance,Initial Balance,Active\n';
      const rows = accounts.map((a) => {
        return `${a.name},${a.type},${a.currency},${a.balance},${a.initialBalance},${a.isActive}`;
      }).join('\n');

      const csv = headers + rows;

      // Save to file
      const fileName = `fincloud_accounts_${new Date().toISOString().split('T')[0]}.csv`;
      const fileUri = FileSystem.documentDirectory + fileName;

      await FileSystem.writeAsStringAsync(fileUri, csv);

      // Share file
      if (await Sharing.isAvailableAsync()) {
        await Sharing.shareAsync(fileUri);
        Alert.alert('Success', 'Accounts exported successfully');
      } else {
        Alert.alert('Success', `File saved to ${fileUri}`);
      }
    } catch (error) {
      console.error('Error exporting accounts:', error);
      Alert.alert('Error', 'Failed to export accounts');
    } finally {
      setExporting(false);
    }
  };

  const exportAllData = async () => {
    Alert.alert(
      'Export All Data',
      'This will export all your financial data to CSV files',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Export',
          onPress: async () => {
            await exportTransactionsCSV();
            await exportAccountsCSV();
          },
        },
      ]
    );
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerIcon}>📤</Text>
        <Text style={styles.headerTitle}>Export Your Data</Text>
        <Text style={styles.headerSubtitle}>
          Export your financial data in CSV format for backup or analysis
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Export Options</Text>

        <TouchableOpacity
          style={styles.exportCard}
          onPress={exportTransactionsCSV}
          disabled={exporting}
        >
          <View style={styles.exportCardHeader}>
            <Text style={styles.exportCardIcon}>💸</Text>
            <View style={styles.exportCardInfo}>
              <Text style={styles.exportCardTitle}>Transactions</Text>
              <Text style={styles.exportCardDescription}>
                All income, expenses, and transfers
              </Text>
            </View>
          </View>
          <Text style={styles.exportCardArrow}>›</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.exportCard}
          onPress={exportAccountsCSV}
          disabled={exporting}
        >
          <View style={styles.exportCardHeader}>
            <Text style={styles.exportCardIcon}>🏦</Text>
            <View style={styles.exportCardInfo}>
              <Text style={styles.exportCardTitle}>Accounts</Text>
              <Text style={styles.exportCardDescription}>
                All your accounts and balances
              </Text>
            </View>
          </View>
          <Text style={styles.exportCardArrow}>›</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.exportCard}
          onPress={exportAllData}
          disabled={exporting}
        >
          <View style={styles.exportCardHeader}>
            <Text style={styles.exportCardIcon}>📦</Text>
            <View style={styles.exportCardInfo}>
              <Text style={styles.exportCardTitle}>All Data</Text>
              <Text style={styles.exportCardDescription}>
                Export everything in one go
              </Text>
            </View>
          </View>
          <Text style={styles.exportCardArrow}>›</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.infoBox}>
        <Text style={styles.infoIcon}>ℹ️</Text>
        <Text style={styles.infoText}>
          Exported files can be opened in spreadsheet applications like Excel,
          Google Sheets, or Numbers.
        </Text>
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
    alignItems: 'center',
    padding: 24,
    backgroundColor: '#fff',
  },
  headerIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  section: {
    marginTop: 16,
    backgroundColor: '#fff',
    padding: 16,
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#999',
    textTransform: 'uppercase',
    marginBottom: 16,
  },
  exportCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#F9F9F9',
    borderRadius: 12,
    marginBottom: 12,
  },
  exportCardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  exportCardIcon: {
    fontSize: 32,
    marginRight: 16,
  },
  exportCardInfo: {
    flex: 1,
  },
  exportCardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  exportCardDescription: {
    fontSize: 12,
    color: '#999',
  },
  exportCardArrow: {
    fontSize: 24,
    color: '#999',
  },
  infoBox: {
    flexDirection: 'row',
    backgroundColor: '#E3F2FF',
    padding: 16,
    margin: 16,
    borderRadius: 8,
  },
  infoIcon: {
    fontSize: 16,
    marginRight: 8,
  },
  infoText: {
    flex: 1,
    fontSize: 12,
    color: '#007AFF',
    lineHeight: 18,
  },
});
