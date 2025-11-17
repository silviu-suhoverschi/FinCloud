import React, { useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, View, ActivityIndicator, Text } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import './src/i18n'; // Initialize i18n
import { database } from './src/storage/database';
import AutoLockProvider from './src/security/AutoLockProvider';
import RootNavigator from './src/navigation/RootNavigator';

export default function App() {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    async function initialize() {
      try {
        // Initialize database
        // Database is already initialized via import, just verify it's ready
        console.log('Database initialized');

        // Initialize app (seed categories, process recurring transactions, etc.)
        const { initializationService } = await import('./src/services/InitializationService');
        await initializationService.initializeApp();

        // Perform daily maintenance if needed
        if (initializationService.shouldPerformDailyMaintenance()) {
          await initializationService.performDailyMaintenance();
        }

        setIsReady(true);
      } catch (error) {
        console.error('Error initializing app:', error);
        // Continue anyway to not block the app
        setIsReady(true);
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
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <AutoLockProvider>
          <RootNavigator />
          <StatusBar style="auto" />
        </AutoLockProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
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
});
