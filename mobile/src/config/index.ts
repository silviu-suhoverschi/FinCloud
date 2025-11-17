/**
 * App configuration
 */

export const Config = {
  // API Configuration
  api: {
    baseUrl: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000',
    timeout: 30000,
  },

  // App Information
  app: {
    name: 'FinCloud',
    version: '1.0.0',
    buildNumber: '1',
  },

  // Security
  security: {
    pinMinLength: 4,
    pinMaxLength: 8,
    defaultAutoLockTimeout: 60, // seconds
    maxLoginAttempts: 5,
  },

  // Storage
  storage: {
    databaseName: 'fincloud',
    encryptionEnabled: true,
  },

  // Sync
  sync: {
    enabled: true,
    interval: 300000, // 5 minutes
    retryAttempts: 3,
    retryDelay: 5000, // 5 seconds
  },

  // External APIs
  externalApis: {
    alphaVantage: {
      apiKey: process.env.EXPO_PUBLIC_ALPHA_VANTAGE_KEY || '',
      baseUrl: 'https://www.alphavantage.co/query',
    },
    coinGecko: {
      apiKey: process.env.EXPO_PUBLIC_COINGECKO_KEY || '',
      baseUrl: 'https://api.coingecko.com/api/v3',
    },
  },

  // Feature Flags
  features: {
    biometricAuth: true,
    portfolioTracking: true,
    multiCurrency: true,
    offlineMode: true,
    darkMode: true,
  },

  // Defaults
  defaults: {
    currency: 'USD',
    language: 'en',
    theme: 'auto',
  },
};

export default Config;
