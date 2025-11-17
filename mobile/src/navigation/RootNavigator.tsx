import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { RootStackParamList } from './types';
import AuthNavigator from './AuthNavigator';
import MainNavigator from './MainNavigator';
import LockScreen from '../screens/auth/LockScreen';
import { useAutoLockContext } from '../security/useAutoLock';
import { mmkvSecureStorage, StorageKeys } from '../storage/mmkv';

const Stack = createStackNavigator<RootStackParamList>();

export default function RootNavigator() {
  const { isLocked } = useAutoLockContext();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      // Check if user has completed onboarding and has auth token
      const hasCompletedOnboarding = mmkvSecureStorage.getBoolean(StorageKeys.HAS_COMPLETED_ONBOARDING);
      const authToken = mmkvSecureStorage.getString(StorageKeys.AUTH_TOKENS);

      setIsAuthenticated(!!hasCompletedOnboarding && !!authToken);
    } catch (error) {
      console.error('Error checking auth status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return null; // Or a loading screen
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {isLocked ? (
          <Stack.Screen name="LockScreen" component={LockScreen} />
        ) : !isAuthenticated ? (
          <Stack.Screen name="Auth" component={AuthNavigator} />
        ) : (
          <Stack.Screen name="Main" component={MainNavigator} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
