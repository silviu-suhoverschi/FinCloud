/**
 * Core type definitions for FinCloud Mobile
 */

// ===== User & Authentication =====
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'user' | 'premium' | 'admin';
  createdAt: Date;
  updatedAt: Date;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
}

// ===== Security =====
export interface SecuritySettings {
  pinEnabled: boolean;
  pinLength: 4 | 6 | 8;
  biometricEnabled: boolean;
  autoLockTimeout: number; // in seconds (0 = disabled, 30, 60, 300, 600)
  lastActivityTimestamp: number;
}

export type BiometricType = 'fingerprint' | 'face' | 'iris' | 'none';

// ===== Accounts =====
export enum AccountType {
  BANK = 'bank',
  SAVINGS = 'savings',
  CASH = 'cash',
  CREDIT = 'credit',
  INVESTMENT = 'investment',
}

export interface Account {
  id: string;
  userId: string;
  name: string;
  type: AccountType;
  currency: string;
  balance: number;
  initialBalance: number;
  description?: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
  syncedAt?: Date;
}

// ===== Transactions =====
export enum TransactionType {
  INCOME = 'income',
  EXPENSE = 'expense',
  TRANSFER = 'transfer',
}

export interface Transaction {
  id: string;
  userId: string;
  accountId: string;
  type: TransactionType;
  amount: number;
  currency: string;
  description: string;
  date: Date;
  categoryId?: string;
  tags: string[];
  recurring: boolean;
  recurringId?: string;
  attachments: string[];
  destinationAccountId?: string; // for transfers
  createdAt: Date;
  updatedAt: Date;
  syncedAt?: Date;
}

// ===== Categories =====
export interface Category {
  id: string;
  userId: string;
  name: string;
  type: TransactionType;
  icon?: string;
  color?: string;
  parentId?: string;
  isDefault: boolean;
  createdAt: Date;
  updatedAt: Date;
  syncedAt?: Date;
}

// ===== Budgets =====
export interface Budget {
  id: string;
  userId: string;
  categoryId: string;
  amount: number;
  currency: string;
  period: 'weekly' | 'monthly' | 'yearly';
  startDate: Date;
  endDate?: Date;
  spent: number;
  createdAt: Date;
  updatedAt: Date;
  syncedAt?: Date;
}

// ===== Portfolio =====
export enum AssetType {
  STOCK = 'stock',
  ETF = 'etf',
  CRYPTO = 'crypto',
  BOND = 'bond',
  COMMODITY = 'commodity',
  REAL_ESTATE = 'real_estate',
}

export interface PortfolioAsset {
  id: string;
  userId: string;
  symbol: string;
  name: string;
  type: AssetType;
  quantity: number;
  averageCost: number;
  currentPrice: number;
  currency: string;
  marketValue: number;
  totalCost: number;
  gainLoss: number;
  gainLossPercentage: number;
  lastPriceUpdate?: Date;
  createdAt: Date;
  updatedAt: Date;
  syncedAt?: Date;
}

export interface PortfolioTransaction {
  id: string;
  userId: string;
  assetId: string;
  type: 'buy' | 'sell' | 'dividend';
  quantity: number;
  price: number;
  fees: number;
  total: number;
  currency: string;
  date: Date;
  notes?: string;
  createdAt: Date;
  updatedAt: Date;
  syncedAt?: Date;
}

// ===== Settings =====
export interface AppSettings {
  language: 'en' | 'ro';
  currency: string;
  theme: 'light' | 'dark' | 'auto';
  notifications: {
    enabled: boolean;
    budgetAlerts: boolean;
    portfolioAlerts: boolean;
    transactionReminders: boolean;
  };
  sync: {
    enabled: boolean;
    wifiOnly: boolean;
    lastSyncAt?: Date;
  };
}

// ===== Sync =====
export interface SyncStatus {
  isOnline: boolean;
  isSyncing: boolean;
  lastSyncAt?: Date;
  lastSyncError?: string;
  pendingChanges: number;
}

export enum SyncOperation {
  CREATE = 'create',
  UPDATE = 'update',
  DELETE = 'delete',
}

export interface SyncQueueItem {
  id: string;
  entityType: string;
  entityId: string;
  operation: SyncOperation;
  data: Record<string, any>;
  createdAt: Date;
  retryCount: number;
  lastError?: string;
}

// ===== API Response Types =====
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// ===== Storage Types =====
export interface StorageConfig {
  encryptionEnabled: boolean;
  version: number;
}
