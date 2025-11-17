import { useEffect, useRef, useState } from 'react';
import { AppState, AppStateStatus } from 'react-native';
import { shouldLockApp, updateLastActivity, isPINEnabled } from './pin';

/**
 * Hook to manage auto-lock functionality
 */
export const useAutoLock = () => {
  const [isLocked, setIsLocked] = useState(false);
  const appState = useRef(AppState.currentState);
  const inactivityTimer = useRef<NodeJS.Timeout | null>(null);

  /**
   * Check if app should be locked
   */
  const checkLockStatus = () => {
    if (isPINEnabled() && shouldLockApp()) {
      setIsLocked(true);
    }
  };

  /**
   * Unlock the app
   */
  const unlock = () => {
    setIsLocked(false);
    updateLastActivity();
    startInactivityTimer();
  };

  /**
   * Lock the app immediately
   */
  const lock = () => {
    setIsLocked(true);
    clearInactivityTimer();
  };

  /**
   * Start inactivity timer
   */
  const startInactivityTimer = () => {
    clearInactivityTimer();

    if (!isPINEnabled()) return;

    // Check lock status every second
    inactivityTimer.current = setInterval(() => {
      checkLockStatus();
    }, 1000);
  };

  /**
   * Clear inactivity timer
   */
  const clearInactivityTimer = () => {
    if (inactivityTimer.current) {
      clearInterval(inactivityTimer.current);
      inactivityTimer.current = null;
    }
  };

  /**
   * Handle app state changes
   */
  const handleAppStateChange = (nextAppState: AppStateStatus) => {
    if (appState.current.match(/inactive|background/) && nextAppState === 'active') {
      // App has come to foreground
      checkLockStatus();
    } else if (nextAppState.match(/inactive|background/)) {
      // App is going to background
      updateLastActivity();
      clearInactivityTimer();
    }

    appState.current = nextAppState;
  };

  useEffect(() => {
    // Check initial lock status
    checkLockStatus();

    // Start inactivity timer if not locked
    if (!isLocked) {
      startInactivityTimer();
    }

    // Subscribe to app state changes
    const subscription = AppState.addEventListener('change', handleAppStateChange);

    return () => {
      subscription.remove();
      clearInactivityTimer();
    };
  }, [isLocked]);

  return {
    isLocked,
    unlock,
    lock,
  };
};
