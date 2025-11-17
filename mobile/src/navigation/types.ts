import { NavigatorScreenParams } from '@react-navigation/native';

// Auth Stack
export type AuthStackParamList = {
  Welcome: undefined;
  Login: undefined;
  Register: undefined;
  PINSetup: { mode: 'create' | 'verify' };
  BiometricSetup: undefined;
};

// Dashboard Stack
export type DashboardStackParamList = {
  DashboardHome: undefined;
};

// Accounts Stack
export type AccountsStackParamList = {
  AccountsList: undefined;
  AccountDetails: { accountId: string };
  AddAccount: undefined;
  EditAccount: { accountId: string };
};

// Transactions Stack
export type TransactionsStackParamList = {
  TransactionsList: undefined;
  TransactionDetails: { transactionId: string };
  AddTransaction: { accountId?: string; type?: 'income' | 'expense' | 'transfer' };
  EditTransaction: { transactionId: string };
};

// Portfolio Stack
export type PortfolioStackParamList = {
  PortfolioHome: undefined;
  AssetDetails: { assetId: string };
  AddAsset: undefined;
  EditAsset: { assetId: string };
  AddPortfolioTransaction: { assetId: string };
};

// More Stack
export type MoreStackParamList = {
  MoreHome: undefined;
  Categories: undefined;
  AddCategory: undefined;
  EditCategory: { categoryId: string };
  Budgets: undefined;
  AddBudget: undefined;
  EditBudget: { budgetId: string };
  Settings: undefined;
  Security: undefined;
  Export: undefined;
};

// Bottom Tabs
export type BottomTabsParamList = {
  Dashboard: NavigatorScreenParams<DashboardStackParamList>;
  Accounts: NavigatorScreenParams<AccountsStackParamList>;
  Transactions: NavigatorScreenParams<TransactionsStackParamList>;
  Portfolio: NavigatorScreenParams<PortfolioStackParamList>;
  More: NavigatorScreenParams<MoreStackParamList>;
};

// Root Stack
export type RootStackParamList = {
  Auth: NavigatorScreenParams<AuthStackParamList>;
  Main: NavigatorScreenParams<BottomTabsParamList>;
  LockScreen: undefined;
};
