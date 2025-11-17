import React, { createContext, useContext, ReactNode } from 'react';
import { useAutoLock } from './useAutoLock';

interface AutoLockContextType {
  isLocked: boolean;
  unlock: () => void;
  lock: () => void;
}

const AutoLockContext = createContext<AutoLockContextType | undefined>(undefined);

interface AutoLockProviderProps {
  children: ReactNode;
}

/**
 * Provider for auto-lock functionality
 * Wrap your app with this provider to enable auto-lock
 */
const AutoLockProvider: React.FC<AutoLockProviderProps> = ({ children }) => {
  const autoLock = useAutoLock();

  return (
    <AutoLockContext.Provider value={autoLock}>
      {children}
    </AutoLockContext.Provider>
  );
};

/**
 * Hook to access auto-lock context
 */
export const useAutoLockContext = (): AutoLockContextType => {
  const context = useContext(AutoLockContext);
  if (!context) {
    throw new Error('useAutoLockContext must be used within AutoLockProvider');
  }
  return context;
};

export default AutoLockProvider;
