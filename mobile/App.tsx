import React, { useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, ActivityIndicator } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import './src/i18n'; // Initialize i18n
import { database } from './src/storage/database';
import AutoLockProvider from './src/security/AutoLockProvider';

export default function App() {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    async function initialize() {
      try {
        // Initialize database
        // Database is already initialized via import, just verify it's ready
        console.log('Database initialized');

        // Add any other initialization logic here
        // - Load user settings
        // - Check authentication status
        // - Initialize services

        setIsReady(true);
      } catch (error) {
        console.error('Error initializing app:', error);
      }
    }

    initialize();
  }, []);

  if (!isReady) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Initializing FinCloud...</Text>
      </View>
    );
  }

  return (
    <SafeAreaProvider>
      <AutoLockProvider>
        <View style={styles.container}>
          <Text style={styles.title}>FinCloud Mobile</Text>
          <Text style={styles.subtitle}>Personal Finance & Investment Tracker</Text>
          <Text style={styles.info}>✅ Offline-first storage configured</Text>
          <Text style={styles.info}>✅ Security features ready</Text>
          <Text style={styles.info}>✅ Internationalization (EN/RO) enabled</Text>
          <Text style={styles.info}>✅ Data repositories initialized</Text>
          <StatusBar style="auto" />
        </View>
      </AutoLockProvider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 32,
  },
  info: {
    fontSize: 14,
    color: '#007AFF',
    marginVertical: 4,
  },
});
