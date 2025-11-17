# FinCloud Mobile

Privacy-first personal finance and investment tracking mobile application built with React Native and Expo.

## 📱 Features

### ✅ Phase 1: Foundation & Platform Setup (Completed)

- **Offline-First Architecture**: Full functionality without internet connection
  - WatermelonDB for local SQLite database
  - MMKV for fast key-value storage
  - Automatic sync when online (planned)

- **Security**
  - PIN Lock (4, 6, or 8 digits)
  - Biometric authentication (Face ID, Touch ID, Fingerprint)
  - AES-256 encryption for sensitive data
  - Configurable auto-lock timer (30s, 1m, 5m, 10m, never)

- **Internationalization**
  - English (EN)
  - Romanian (RO)
  - Easy to add more languages

- **Data Management**
  - Accounts (Bank, Savings, Cash, Credit Card, Investment)
  - Transactions (Income, Expense, Transfer)
  - Categories with subcategories
  - Budgets (Weekly, Monthly, Yearly)
  - Portfolio tracking (Stocks, ETF, Crypto, Bonds)

### ✅ Phase 2: Core FREE (MVP) Features (Completed)

- **Transactions Management**
  - Add/edit/delete transaction flows with validation
  - Receipt photo attachments using expo-image-picker
  - Transfer transactions between accounts
  - Soft-delete markers for future sync
  - Tag support for better organization
  - Search and filter functionality

- **Recurring Transactions**
  - Daily, weekly, monthly, and yearly scheduling
  - Configurable intervals (e.g., every 2 weeks)
  - Automatic transaction creation engine
  - End date support (optional)
  - Active/inactive toggle

- **Categories**
  - 20 preset localized categories (10 expense, 5 income)
  - Custom category creation with CRUD operations
  - Icon picker (12 preset icons: 💼, 💻, 📈, 🎁, 💰, 🍽️, 🛒, 🚗, 💡, 🏠, 🏥, ...)
  - Color picker (12 preset colors)
  - Live preview in forms
  - Default category protection

- **Accounts (Wallets)**
  - 5 account types: Bank, Savings, Cash, Credit Card, Investment
  - FREE tier enforcement: max 5 accounts
  - Opening balance support
  - Multi-currency support (USD, EUR, GBP, RON, JPY, CAD, AUD)
  - Account activation/deactivation (archive)
  - Rename and edit functionality
  - Transaction history per account

- **Budgets**
  - Create budgets with weekly/monthly/annual periods
  - Progress bars showing spent vs. remaining
  - Category-based budgeting
  - Overspending indicators (visual warnings)
  - Automatic spending calculations

- **Budget Notifications**
  - 80% warning threshold
  - 100% budget exceeded alert
  - 120% overspending notification
  - Push notifications via expo-notifications
  - Configurable on/off in settings

- **Dashboard**
  - Total balance aggregation across accounts
  - Income/Expense totals for current month
  - Category pie chart using react-native-chart-kit
  - 7-day spending trend line chart
  - Recent transactions list (last 5)
  - Pull-to-refresh functionality

- **Portfolio (Manual)**
  - 6 asset types: Stock, ETF, Crypto, Bond, Commodity, Real Estate
  - Manual price entry
  - Yahoo Finance price refresh integration
  - Performance metrics (quantity, avg cost, current price, gain/loss)
  - Transaction history (buy/sell/dividend)
  - Total portfolio value calculation

- **Yahoo Finance Integration**
  - Real-time price fetching for stocks/ETFs
  - Batch price updates with rate limiting
  - Symbol search functionality
  - CoinGecko fallback for crypto prices
  - Automatic portfolio value updates

- **Localization & Export**
  - Language switcher (English/Romanian)
  - Auto-detect with fallback
  - All 20 preset categories localized
  - CSV export for:
    - Transactions
    - Accounts
    - Categories
    - Budgets
    - Portfolio assets
    - All data (combined export)
  - File sharing via expo-sharing

## 🏗️ Architecture

### Project Structure

```
mobile/
├── src/
│   ├── components/      # Reusable UI components
│   ├── screens/         # Screen components
│   ├── navigation/      # Navigation configuration
│   ├── services/        # Business logic services
│   ├── storage/         # Database & storage layer
│   │   ├── database.ts  # WatermelonDB configuration
│   │   ├── schema.ts    # Database schema
│   │   └── mmkv.ts      # MMKV key-value storage
│   ├── repositories/    # Data access layer
│   │   ├── AccountRepository.ts
│   │   ├── TransactionRepository.ts
│   │   ├── CategoryRepository.ts
│   │   ├── BudgetRepository.ts
│   │   └── PortfolioRepository.ts
│   ├── models/          # WatermelonDB models
│   │   ├── Account.ts
│   │   ├── Transaction.ts
│   │   ├── Category.ts
│   │   ├── Budget.ts
│   │   ├── PortfolioAsset.ts
│   │   └── PortfolioTransaction.ts
│   ├── security/        # Security utilities
│   │   ├── encryption.ts          # AES-256 encryption
│   │   ├── pin.ts                 # PIN lock system
│   │   ├── biometric.ts           # Biometric auth
│   │   ├── AutoLockProvider.tsx   # Auto-lock provider
│   │   └── useAutoLock.ts         # Auto-lock hook
│   ├── i18n/            # Internationalization
│   │   ├── index.ts
│   │   └── locales/
│   │       ├── en.json
│   │       └── ro.json
│   ├── config/          # App configuration
│   ├── types/           # TypeScript definitions
│   ├── utils/           # Utility functions
│   ├── hooks/           # Custom React hooks
│   └── store/           # State management (Zustand)
├── assets/              # Images, fonts, etc.
├── App.tsx             # Main app component
├── package.json
└── tsconfig.json
```

### Technology Stack

- **Framework**: React Native + Expo (SDK 54)
- **Language**: TypeScript
- **Database**: WatermelonDB (SQLite)
- **Storage**: MMKV (fast key-value storage)
- **State Management**: Zustand (planned)
- **Navigation**: React Navigation
- **Internationalization**: i18next + react-i18next
- **Security**:
  - expo-crypto (hashing, key derivation)
  - expo-local-authentication (biometric)
  - expo-secure-store (secure storage)

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Expo CLI (`npm install -g expo-cli`)
- iOS Simulator (Mac only) or Android Emulator
- For physical devices: Expo Go app

### Installation

1. Navigate to the mobile directory:
   ```bash
   cd mobile
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create environment file:
   ```bash
   cp .env.example .env
   ```

4. Update `.env` with your configuration:
   ```env
   EXPO_PUBLIC_API_URL=http://localhost:8000
   EXPO_PUBLIC_ALPHA_VANTAGE_KEY=your_key_here
   EXPO_PUBLIC_COINGECKO_KEY=your_key_here
   ```

### Running the App

```bash
# Start Expo development server
npm start

# Run on iOS simulator (Mac only)
npm run ios

# Run on Android emulator
npm run android

# Run in web browser
npm run web

# Clear cache and restart
npm run clear
```

### Development Commands

```bash
# Type checking
npm run type-check

# Linting (when configured)
npm run lint

# Code formatting (when configured)
npm run format
```

## 🔐 Security Features

### PIN Lock

The app supports PIN protection with configurable length (4, 6, or 8 digits):

```typescript
import { PINService } from './src/security';

// Set up a new PIN
await PINService.setupPIN('1234', 4);

// Verify PIN
const isValid = await PINService.verifyPINCode('1234');

// Change PIN
await PINService.changePIN('1234', '5678');

// Disable PIN
await PINService.disablePIN('1234');
```

### Biometric Authentication

Supports Face ID, Touch ID, and Fingerprint:

```typescript
import { BiometricService } from './src/security';

// Check if biometric is available
const isSupported = await BiometricService.isBiometricSupported();

// Enable biometric authentication
const result = await BiometricService.enableBiometric();

// Authenticate with biometrics
const auth = await BiometricService.authenticateWithBiometrics('Unlock FinCloud');
```

### Auto-Lock

Automatically locks the app after a period of inactivity:

```typescript
import { useAutoLockContext } from './src/security';

function MyComponent() {
  const { isLocked, unlock, lock } = useAutoLockContext();

  // Lock the app immediately
  lock();

  // Unlock after authentication
  unlock();
}
```

### Encryption

AES-256 encryption helpers for sensitive data:

```typescript
import { SecurityUtils } from './src/security';

// Hash a PIN
const { hash, salt } = await SecurityUtils.hashPIN('1234');

// Verify a PIN
const isValid = await SecurityUtils.verifyPIN('1234', hash, salt);

// Generate encryption key
const key = await SecurityUtils.generateEncryptionKey();
```

## 🗄️ Data Layer

### Repositories

Use repositories to interact with the database:

```typescript
import {
  accountRepository,
  transactionRepository,
  categoryRepository,
  budgetRepository,
  portfolioAssetRepository,
} from './src/repositories';

// Create an account
const account = await accountRepository.create({
  userId: 'user123',
  name: 'Checking Account',
  type: AccountType.BANK,
  currency: 'USD',
  balance: 1000,
  initialBalance: 1000,
  isActive: true,
});

// Get all accounts for a user
const accounts = await accountRepository.getByUserId('user123');

// Update account balance
await accountRepository.updateBalance(account.id, 100);

// Create a transaction
const transaction = await transactionRepository.create({
  userId: 'user123',
  accountId: account.id,
  type: TransactionType.EXPENSE,
  amount: 50,
  currency: 'USD',
  description: 'Groceries',
  date: new Date(),
  tags: ['food', 'groceries'],
  recurring: false,
  attachments: [],
});

// Get transactions by date range
const transactions = await transactionRepository.getByDateRange(
  'user123',
  new Date('2025-01-01'),
  new Date('2025-01-31')
);
```

### Storage

MMKV for fast key-value storage:

```typescript
import { mmkvStorage, mmkvSecureStorage, StorageKeys } from './src/storage/mmkv';

// Regular storage
mmkvStorage.set('theme', 'dark');
const theme = mmkvStorage.getString('theme');

// Store objects
mmkvStorage.setObject('settings', { notifications: true });
const settings = mmkvStorage.getObject('settings');

// Secure storage (encrypted)
mmkvSecureStorage.set(StorageKeys.AUTH_TOKENS, 'token123');
const token = mmkvSecureStorage.get(StorageKeys.AUTH_TOKENS);
```

## 🌍 Internationalization

The app supports multiple languages using i18next:

```typescript
import { useTranslation } from 'react-i18next';
import { changeLanguage } from './src/i18n';

function MyComponent() {
  const { t } = useTranslation();

  return (
    <View>
      <Text>{t('common.appName')}</Text>
      <Text>{t('accounts.addAccount')}</Text>
    </View>
  );
}

// Change language
changeLanguage('ro'); // Switch to Romanian
changeLanguage('en'); // Switch to English
```

### Adding Translations

Edit the locale files in `src/i18n/locales/`:

- `en.json` - English translations
- `ro.json` - Romanian translations

## 📊 Database Schema

The app uses WatermelonDB with the following tables:

- **accounts**: User bank accounts, credit cards, etc.
- **transactions**: Income, expenses, and transfers
- **categories**: Transaction categories
- **budgets**: Budget allocations by category
- **portfolio_assets**: Investment assets (stocks, crypto, etc.)
- **portfolio_transactions**: Buy/sell transactions for assets

Each table includes:
- `user_id`: Links to the authenticated user
- `created_at`: Creation timestamp
- `updated_at`: Last modification timestamp
- `synced_at`: Last sync timestamp (for offline sync)

## 🔄 Offline-First & Sync

The app is designed to work fully offline:

1. **Local-First**: All data is stored locally first
2. **Background Sync**: Changes sync automatically when online
3. **Conflict Resolution**: Last-write-wins strategy (can be customized)
4. **Sync Queue**: Failed syncs are retried automatically

## 📝 Implementation Details

### Screens Implemented (27 total)

**Auth Flow (3 screens)**
- `WelcomeScreen` - App introduction and onboarding
- `PINSetupScreen` - PIN creation with 4/6/8 digit support
- `BiometricSetupScreen` - Biometric authentication setup
- `LockScreen` - App lock/unlock screen

**Dashboard (1 screen)**
- `DashboardScreen` - Main overview with balance, charts, and recent transactions

**Accounts (4 screens)**
- `AccountsListScreen` - List all accounts with total balance
- `AccountDetailsScreen` - Individual account with transaction history
- `AddAccountScreen` - Create account with FREE tier check (max 5)
- `EditAccountScreen` - Edit account details and archive

**Transactions (4 screens)**
- `TransactionsListScreen` - Searchable, filterable transaction list
- `TransactionDetailsScreen` - Transaction details with attachments
- `AddTransactionScreen` - Add income/expense/transfer with photo
- `EditTransactionScreen` - Edit transaction

**Portfolio (5 screens)**
- `PortfolioScreen` - Asset overview with total value
- `AssetDetailsScreen` - Asset details with performance metrics
- `AddAssetScreen` - Add investment asset
- `EditAssetScreen` - Edit asset details
- `AddPortfolioTransactionScreen` - Record buy/sell/dividend

**More & Settings (10 screens)**
- `MoreScreen` - Settings menu hub
- `CategoriesScreen` - Manage categories
- `AddCategoryScreen` - Create category with icon/color picker
- `EditCategoryScreen` - Edit category
- `BudgetsScreen` - Budget list with progress bars
- `AddBudgetScreen` - Create budget
- `EditBudgetScreen` - Edit budget
- `SettingsScreen` - App preferences (language, theme, currency, etc.)
- `SecurityScreen` - Security settings (PIN, biometric, auto-lock)
- `ExportScreen` - CSV data export

### Services Implemented

**RecurringTransactionService**
- Manages recurring transaction patterns
- Calculates next execution dates
- Processes due transactions automatically
- Supports daily, weekly, monthly, yearly frequencies

**CategorySeedService**
- Seeds 20 preset categories on first launch
- Localized for EN/RO
- Prevents duplicate seeding
- Supports re-seeding with language change

**NotificationService**
- Budget overspending alerts (80%, 100%, 120%)
- Notification permission handling
- Configurable on/off via settings
- Recurring transaction reminders (planned)

**PriceUpdateService**
- Yahoo Finance API integration
- Batch price updates with rate limiting
- Symbol search functionality
- CoinGecko crypto price fallback
- Automatic portfolio recalculation

**InitializationService**
- First launch setup and configuration
- Category seeding orchestration
- Daily maintenance tasks (recurring transactions, budget alerts)
- Onboarding state management

### Key Features

**FREE Tier Enforcement**
- Maximum 5 accounts per user
- Implemented in `AddAccountScreen:155-161`
- Shows helpful upgrade message
- Prevents account creation when limit reached

**Preset Categories (20 total)**

*Income (5)*:
- 💼 Salary - 💻 Freelance - 📈 Investment - 🎁 Gift - 💰 Other Income

*Expense (15)*:
- 🍽️ Food & Dining - 🛒 Groceries - 🚗 Transportation - 💡 Utilities
- 🏠 Housing - 🏥 Healthcare - 🎬 Entertainment - 🛍️ Shopping
- ✈️ Travel - 📚 Education - 💆 Personal Care - 🛡️ Insurance
- 📱 Subscriptions - 🐾 Pet Care - 💸 Other Expenses

**Multi-Currency Support**
- USD, EUR, GBP, RON, JPY, CAD, AUD
- Per-account currency settings
- Portfolio supports mixed currencies

**Transaction Types**
- **Income**: Money received (salary, freelance, gifts, etc.)
- **Expense**: Money spent (groceries, bills, shopping, etc.)
- **Transfer**: Move money between accounts (updates both balances)

**Budget Periods**
- Weekly: 7-day rolling period
- Monthly: Calendar month
- Yearly: Calendar year

**Asset Types**
- Stock - ETF - Crypto - Bond - Commodity (Gold, Silver, etc.) - Real Estate

## 📝 Next Steps

### Phase 3: Enhancements
- [ ] Add recurring transaction management screen
- [ ] Implement data import (CSV, OFX, QIF)
- [ ] Advanced filtering and date range selection
- [ ] Reports and analytics screens
- [ ] Budget rollover functionality
- [ ] Multi-account transfers

### Phase 4: Sync & Cloud (Future)
- [ ] API integration with backend services
- [ ] Sync engine with conflict resolution
- [ ] Offline queue management
- [ ] Cloud backup and restore
- [ ] Multi-device support

## 🤝 Contributing

See the main project [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## 📄 License

See the main project [LICENSE](../LICENSE) file.

## 🔗 Related Documentation

- [Backend Services](../services/README.md)
- [API Documentation](../services/api-gateway/API_GATEWAY_README.md)
- [Project Overview](../README.md)

## 💡 Notes

### Security Considerations

- **Encryption**: The current encryption implementation uses basic encoding as a placeholder. For production, implement proper AES-256-GCM encryption using:
  - Web Crypto API (for web)
  - Native modules (react-native-aes-crypto)
  - Or use expo-secure-store for sensitive data storage

- **PIN Storage**: PINs are hashed using SHA-256 with a salt before storage
- **Biometric**: Uses device-native biometric authentication
- **Auto-Lock**: Configurable timeout to protect data when app is inactive

### Performance

- **WatermelonDB**: Optimized for 10,000+ records with lazy loading
- **MMKV**: 10-30x faster than AsyncStorage
- **JSI**: Uses JavaScript Interface for direct native access (React Native 0.68+)

### Expo Limitations

Some features may require custom development builds (not available in Expo Go):
- Native modules for AES encryption
- Custom native code
- Some advanced biometric features

Use `eas build` to create custom development builds if needed.
