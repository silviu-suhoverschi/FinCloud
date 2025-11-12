# Database Schema Design

> Version: 1.0
> Last Updated: 2025-11-12
> Status: Design Phase

## Overview

FinCloud uses PostgreSQL as its primary database with a **schema-per-service** approach. Each microservice maintains its own database schema for better isolation, scalability, and independent deployments.

### Database Architecture

- **Budget Service**: `budget_db` - Handles accounts, transactions, budgets, and categories
- **Portfolio Service**: `portfolio_db` - Manages portfolios, holdings, assets, and price data
- **Shared**: User authentication data managed by API Gateway, referenced via `user_id`

### Design Principles

1. **Normalization**: Follow 3NF (Third Normal Form) with strategic denormalization for performance
2. **Soft Deletes**: Use `deleted_at` timestamps instead of hard deletes for audit trail
3. **Timestamps**: All tables include `created_at` and `updated_at`
4. **UUIDs**: Primary keys use BIGINT/SERIAL for performance; UUIDs available for external references
5. **Foreign Keys**: Enforce referential integrity with appropriate CASCADE rules
6. **Indexes**: Strategic indexing for common query patterns
7. **Constraints**: Database-level validation for data integrity

---

## Budget Service Schema

### 1. Users Table

Stores user account information and authentication data.

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMP,
    last_login_at TIMESTAMP,
    preferred_currency VARCHAR(3) DEFAULT 'USD',
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_uuid ON users(uuid);
CREATE INDEX idx_users_is_active ON users(is_active) WHERE deleted_at IS NULL;

-- Constraints
ALTER TABLE users ADD CONSTRAINT chk_email_format
    CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');
ALTER TABLE users ADD CONSTRAINT chk_preferred_currency_length
    CHECK (LENGTH(preferred_currency) = 3);
```

**Fields:**
- `id`: Internal primary key
- `uuid`: External reference ID for API responses
- `email`: Unique email address (indexed)
- `password_hash`: Bcrypt hashed password
- `is_active`: Account status flag
- `is_verified`: Email verification status
- `preferred_currency`: Default currency (ISO 4217 code)
- `timezone`: User's timezone for date calculations

---

### 2. Accounts Table

Financial accounts (bank, credit card, cash, investment, etc.).

```sql
CREATE TABLE accounts (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    initial_balance DECIMAL(15, 2) NOT NULL DEFAULT 0,
    current_balance DECIMAL(15, 2) NOT NULL DEFAULT 0,
    account_number VARCHAR(100),
    institution VARCHAR(255),
    color VARCHAR(7),
    icon VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    include_in_net_worth BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_accounts_user_id ON accounts(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_accounts_type ON accounts(type);
CREATE INDEX idx_accounts_is_active ON accounts(is_active);
CREATE INDEX idx_accounts_created_at ON accounts(created_at);

-- Constraints
ALTER TABLE accounts ADD CONSTRAINT chk_account_type
    CHECK (type IN ('checking', 'savings', 'credit_card', 'cash', 'investment', 'loan', 'mortgage', 'other'));
ALTER TABLE accounts ADD CONSTRAINT chk_currency_length
    CHECK (LENGTH(currency) = 3);
ALTER TABLE accounts ADD CONSTRAINT chk_color_format
    CHECK (color IS NULL OR color ~* '^#[0-9A-Fa-f]{6}$');
ALTER TABLE accounts ADD CONSTRAINT chk_balance_precision
    CHECK (current_balance > -999999999999.99 AND current_balance < 999999999999.99);
```

**Account Types:**
- `checking`: Standard checking account
- `savings`: Savings account
- `credit_card`: Credit card account (negative balance)
- `cash`: Physical cash
- `investment`: Investment/brokerage account
- `loan`: Loan account
- `mortgage`: Mortgage account
- `other`: Other account types

---

### 3. Categories Table

Transaction categories with hierarchical support (parent-child relationships).

```sql
CREATE TABLE categories (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parent_id BIGINT REFERENCES categories(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    color VARCHAR(7),
    icon VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,
    UNIQUE(user_id, name, parent_id)
);

-- Indexes
CREATE INDEX idx_categories_user_id ON categories(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_categories_parent_id ON categories(parent_id);
CREATE INDEX idx_categories_type ON categories(type);
CREATE INDEX idx_categories_sort_order ON categories(sort_order);

-- Constraints
ALTER TABLE categories ADD CONSTRAINT chk_category_type
    CHECK (type IN ('income', 'expense', 'transfer'));
ALTER TABLE categories ADD CONSTRAINT chk_no_self_reference
    CHECK (id != parent_id);
```

**Category Types:**
- `income`: Income categories (salary, dividends, etc.)
- `expense`: Expense categories (groceries, utilities, etc.)
- `transfer`: Transfer between accounts

**Hierarchical Structure:**
- Parent categories: `parent_id` is NULL
- Child categories: `parent_id` references parent category
- Example: "Food" (parent) → "Groceries" (child), "Dining Out" (child)

---

### 4. Transactions Table

Financial transactions (income, expenses, transfers).

```sql
CREATE TABLE transactions (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_id BIGINT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    category_id BIGINT REFERENCES categories(id) ON DELETE SET NULL,
    destination_account_id BIGINT REFERENCES accounts(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    exchange_rate DECIMAL(15, 6) DEFAULT 1.0,
    date DATE NOT NULL,
    description TEXT NOT NULL,
    payee VARCHAR(255),
    reference_number VARCHAR(100),
    notes TEXT,
    tags TEXT[],
    is_reconciled BOOLEAN DEFAULT FALSE,
    reconciled_at TIMESTAMP,
    recurring_transaction_id BIGINT,
    external_id VARCHAR(255),
    import_source VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_transactions_user_id ON transactions(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_transactions_account_id ON transactions(account_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_transactions_category_id ON transactions(category_id);
CREATE INDEX idx_transactions_date ON transactions(date DESC);
CREATE INDEX idx_transactions_type ON transactions(type);
CREATE INDEX idx_transactions_created_at ON transactions(created_at DESC);
CREATE INDEX idx_transactions_payee ON transactions(payee) WHERE payee IS NOT NULL;
CREATE INDEX idx_transactions_tags ON transactions USING GIN(tags);
CREATE INDEX idx_transactions_external_id ON transactions(external_id) WHERE external_id IS NOT NULL;

-- Full-text search index
CREATE INDEX idx_transactions_search ON transactions
    USING GIN(to_tsvector('english', COALESCE(description, '') || ' ' || COALESCE(payee, '') || ' ' || COALESCE(notes, '')));

-- Constraints
ALTER TABLE transactions ADD CONSTRAINT chk_transaction_type
    CHECK (type IN ('income', 'expense', 'transfer'));
ALTER TABLE transactions ADD CONSTRAINT chk_amount_positive
    CHECK (amount > 0);
ALTER TABLE transactions ADD CONSTRAINT chk_transfer_has_destination
    CHECK (type != 'transfer' OR destination_account_id IS NOT NULL);
ALTER TABLE transactions ADD CONSTRAINT chk_no_self_transfer
    CHECK (account_id != destination_account_id);
ALTER TABLE transactions ADD CONSTRAINT chk_exchange_rate_positive
    CHECK (exchange_rate > 0);
```

**Transaction Types:**
- `income`: Money coming in
- `expense`: Money going out
- `transfer`: Transfer between accounts (requires `destination_account_id`)

**Special Fields:**
- `tags`: Array of tags for flexible categorization
- `external_id`: For imported transactions (bank feed, CSV)
- `exchange_rate`: For multi-currency transactions
- `is_reconciled`: Bank reconciliation flag

---

### 5. Budgets Table

Budget allocations for categories or accounts.

```sql
CREATE TABLE budgets (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id BIGINT REFERENCES categories(id) ON DELETE CASCADE,
    account_id BIGINT REFERENCES accounts(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    period VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    rollover_unused BOOLEAN DEFAULT FALSE,
    alert_enabled BOOLEAN DEFAULT TRUE,
    alert_threshold DECIMAL(5, 2) DEFAULT 80.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,
    CHECK (category_id IS NOT NULL OR account_id IS NOT NULL)
);

-- Indexes
CREATE INDEX idx_budgets_user_id ON budgets(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_budgets_category_id ON budgets(category_id);
CREATE INDEX idx_budgets_account_id ON budgets(account_id);
CREATE INDEX idx_budgets_period ON budgets(period);
CREATE INDEX idx_budgets_start_date ON budgets(start_date);
CREATE INDEX idx_budgets_is_active ON budgets(is_active);

-- Constraints
ALTER TABLE budgets ADD CONSTRAINT chk_budget_period
    CHECK (period IN ('daily', 'weekly', 'monthly', 'quarterly', 'yearly', 'custom'));
ALTER TABLE budgets ADD CONSTRAINT chk_amount_positive
    CHECK (amount > 0);
ALTER TABLE budgets ADD CONSTRAINT chk_alert_threshold_range
    CHECK (alert_threshold >= 0 AND alert_threshold <= 100);
ALTER TABLE budgets ADD CONSTRAINT chk_end_date_after_start
    CHECK (end_date IS NULL OR end_date >= start_date);
```

**Budget Periods:**
- `daily`: Daily budget
- `weekly`: Weekly budget
- `monthly`: Monthly budget
- `quarterly`: Quarterly budget
- `yearly`: Annual budget
- `custom`: Custom period (use `start_date` and `end_date`)

---

### 6. Recurring Transactions Table

Templates for recurring transactions (subscriptions, salaries, etc.).

```sql
CREATE TABLE recurring_transactions (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_id BIGINT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    category_id BIGINT REFERENCES categories(id) ON DELETE SET NULL,
    destination_account_id BIGINT REFERENCES accounts(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    description TEXT NOT NULL,
    payee VARCHAR(255),
    frequency VARCHAR(50) NOT NULL,
    interval_count INTEGER DEFAULT 1,
    start_date DATE NOT NULL,
    end_date DATE,
    next_occurrence DATE NOT NULL,
    last_generated_at TIMESTAMP,
    occurrences_count INTEGER DEFAULT 0,
    max_occurrences INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    auto_create BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_recurring_transactions_user_id ON recurring_transactions(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_recurring_transactions_account_id ON recurring_transactions(account_id);
CREATE INDEX idx_recurring_transactions_next_occurrence ON recurring_transactions(next_occurrence)
    WHERE is_active = TRUE AND deleted_at IS NULL;
CREATE INDEX idx_recurring_transactions_is_active ON recurring_transactions(is_active);

-- Constraints
ALTER TABLE recurring_transactions ADD CONSTRAINT chk_recurring_type
    CHECK (type IN ('income', 'expense', 'transfer'));
ALTER TABLE recurring_transactions ADD CONSTRAINT chk_recurring_frequency
    CHECK (frequency IN ('daily', 'weekly', 'biweekly', 'monthly', 'quarterly', 'yearly'));
ALTER TABLE recurring_transactions ADD CONSTRAINT chk_interval_positive
    CHECK (interval_count > 0);
ALTER TABLE recurring_transactions ADD CONSTRAINT chk_recurring_amount_positive
    CHECK (amount > 0);
```

**Frequency Types:**
- `daily`: Every N days
- `weekly`: Every N weeks
- `biweekly`: Every 2 weeks
- `monthly`: Every N months
- `quarterly`: Every 3 months
- `yearly`: Every N years

---

### 7. Tags Table

Reusable tags for transactions and budgets.

```sql
CREATE TABLE tags (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7),
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, name)
);

-- Indexes
CREATE INDEX idx_tags_user_id ON tags(user_id);
CREATE INDEX idx_tags_usage_count ON tags(usage_count DESC);
```

---

### 8. Budget Spending Cache Table

Denormalized table for fast budget progress queries.

```sql
CREATE TABLE budget_spending_cache (
    id BIGSERIAL PRIMARY KEY,
    budget_id BIGINT NOT NULL REFERENCES budgets(id) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_spent DECIMAL(15, 2) DEFAULT 0,
    total_budget DECIMAL(15, 2) NOT NULL,
    transaction_count INTEGER DEFAULT 0,
    last_calculated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(budget_id, period_start)
);

-- Indexes
CREATE INDEX idx_budget_spending_cache_budget_id ON budget_spending_cache(budget_id);
CREATE INDEX idx_budget_spending_cache_period ON budget_spending_cache(period_start, period_end);
```

---

## Portfolio Service Schema

### 1. Portfolios Table

Investment portfolios owned by users.

```sql
CREATE TABLE portfolios (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,
    UNIQUE(user_id, name)
);

-- Indexes
CREATE INDEX idx_portfolios_user_id ON portfolios(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_portfolios_is_active ON portfolios(is_active);
CREATE INDEX idx_portfolios_sort_order ON portfolios(sort_order);
```

---

### 2. Assets Table

Investment assets (stocks, ETFs, crypto, bonds, etc.).

```sql
CREATE TABLE assets (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    asset_class VARCHAR(50),
    sector VARCHAR(100),
    exchange VARCHAR(100),
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    isin VARCHAR(12),
    cusip VARCHAR(9),
    figi VARCHAR(12),
    country VARCHAR(3),
    logo_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,
    UNIQUE(symbol, exchange)
);

-- Indexes
CREATE INDEX idx_assets_symbol ON assets(symbol) WHERE deleted_at IS NULL;
CREATE INDEX idx_assets_type ON assets(type);
CREATE INDEX idx_assets_asset_class ON assets(asset_class);
CREATE INDEX idx_assets_sector ON assets(sector);
CREATE INDEX idx_assets_isin ON assets(isin) WHERE isin IS NOT NULL;
CREATE INDEX idx_assets_metadata ON assets USING GIN(metadata);

-- Full-text search
CREATE INDEX idx_assets_search ON assets
    USING GIN(to_tsvector('english', name || ' ' || symbol));

-- Constraints
ALTER TABLE assets ADD CONSTRAINT chk_asset_type
    CHECK (type IN ('stock', 'etf', 'mutual_fund', 'crypto', 'bond', 'commodity', 'index', 'other'));
ALTER TABLE assets ADD CONSTRAINT chk_asset_class
    CHECK (asset_class IS NULL OR asset_class IN ('equity', 'fixed_income', 'real_estate', 'commodity', 'cash', 'alternative', 'cryptocurrency'));
ALTER TABLE assets ADD CONSTRAINT chk_isin_format
    CHECK (isin IS NULL OR isin ~* '^[A-Z]{2}[A-Z0-9]{9}[0-9]$');
ALTER TABLE assets ADD CONSTRAINT chk_country_code
    CHECK (country IS NULL OR LENGTH(country) = 3);
```

**Asset Types:**
- `stock`: Individual stocks
- `etf`: Exchange-traded funds
- `mutual_fund`: Mutual funds
- `crypto`: Cryptocurrencies
- `bond`: Bonds
- `commodity`: Commodities (gold, oil, etc.)
- `index`: Market indexes
- `other`: Other asset types

**Asset Classes:**
- `equity`: Stocks, ETFs
- `fixed_income`: Bonds
- `real_estate`: REITs
- `commodity`: Commodities
- `cash`: Cash equivalents
- `alternative`: Alternative investments
- `cryptocurrency`: Digital currencies

---

### 3. Holdings Table

Current holdings in portfolios.

```sql
CREATE TABLE holdings (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    portfolio_id BIGINT NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    asset_id BIGINT NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    quantity DECIMAL(20, 8) NOT NULL DEFAULT 0,
    average_cost DECIMAL(15, 4) NOT NULL DEFAULT 0,
    cost_basis DECIMAL(15, 2) NOT NULL DEFAULT 0,
    current_price DECIMAL(15, 4),
    current_value DECIMAL(15, 2),
    unrealized_gain_loss DECIMAL(15, 2),
    unrealized_gain_loss_percent DECIMAL(10, 4),
    last_price_update TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,
    UNIQUE(portfolio_id, asset_id)
);

-- Indexes
CREATE INDEX idx_holdings_portfolio_id ON holdings(portfolio_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_holdings_asset_id ON holdings(asset_id);
CREATE INDEX idx_holdings_quantity ON holdings(quantity) WHERE quantity > 0;

-- Constraints
ALTER TABLE holdings ADD CONSTRAINT chk_average_cost_non_negative
    CHECK (average_cost >= 0);
ALTER TABLE holdings ADD CONSTRAINT chk_cost_basis_non_negative
    CHECK (cost_basis >= 0);
```

**Calculated Fields:**
- `cost_basis = quantity * average_cost`
- `current_value = quantity * current_price`
- `unrealized_gain_loss = current_value - cost_basis`
- `unrealized_gain_loss_percent = (unrealized_gain_loss / cost_basis) * 100`

---

### 4. Portfolio Transactions Table

Buy, sell, dividend, and other portfolio transactions.

```sql
CREATE TABLE portfolio_transactions (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    portfolio_id BIGINT NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    asset_id BIGINT NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    quantity DECIMAL(20, 8) NOT NULL,
    price DECIMAL(15, 4) NOT NULL,
    total_amount DECIMAL(15, 2) NOT NULL,
    fee DECIMAL(15, 2) DEFAULT 0,
    tax DECIMAL(15, 2) DEFAULT 0,
    currency VARCHAR(3) NOT NULL,
    exchange_rate DECIMAL(15, 6) DEFAULT 1.0,
    date DATE NOT NULL,
    notes TEXT,
    reference_number VARCHAR(100),
    external_id VARCHAR(255),
    import_source VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_portfolio_transactions_portfolio_id ON portfolio_transactions(portfolio_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_portfolio_transactions_asset_id ON portfolio_transactions(asset_id);
CREATE INDEX idx_portfolio_transactions_type ON portfolio_transactions(type);
CREATE INDEX idx_portfolio_transactions_date ON portfolio_transactions(date DESC);
CREATE INDEX idx_portfolio_transactions_created_at ON portfolio_transactions(created_at DESC);

-- Constraints
ALTER TABLE portfolio_transactions ADD CONSTRAINT chk_portfolio_transaction_type
    CHECK (type IN ('buy', 'sell', 'dividend', 'interest', 'fee', 'tax', 'split', 'transfer_in', 'transfer_out'));
ALTER TABLE portfolio_transactions ADD CONSTRAINT chk_quantity_positive
    CHECK (quantity > 0 OR type IN ('fee', 'tax'));
ALTER TABLE portfolio_transactions ADD CONSTRAINT chk_price_non_negative
    CHECK (price >= 0);
ALTER TABLE portfolio_transactions ADD CONSTRAINT chk_fee_non_negative
    CHECK (fee >= 0);
ALTER TABLE portfolio_transactions ADD CONSTRAINT chk_tax_non_negative
    CHECK (tax >= 0);
```

**Transaction Types:**
- `buy`: Purchase of assets
- `sell`: Sale of assets
- `dividend`: Dividend payment
- `interest`: Interest payment
- `fee`: Transaction fee
- `tax`: Tax payment
- `split`: Stock split
- `transfer_in`: Transfer into portfolio
- `transfer_out`: Transfer out of portfolio

---

### 5. Price History Table

Historical price data for assets.

```sql
CREATE TABLE price_history (
    id BIGSERIAL PRIMARY KEY,
    asset_id BIGINT NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    open DECIMAL(15, 4),
    high DECIMAL(15, 4),
    low DECIMAL(15, 4),
    close DECIMAL(15, 4) NOT NULL,
    adjusted_close DECIMAL(15, 4),
    volume BIGINT,
    source VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(asset_id, date, source)
);

-- Indexes
CREATE INDEX idx_price_history_asset_id ON price_history(asset_id);
CREATE INDEX idx_price_history_date ON price_history(date DESC);
CREATE INDEX idx_price_history_asset_date ON price_history(asset_id, date DESC);
CREATE INDEX idx_price_history_source ON price_history(source);

-- Constraints
ALTER TABLE price_history ADD CONSTRAINT chk_ohlc_positive
    CHECK (open > 0 OR open IS NULL);
ALTER TABLE price_history ADD CONSTRAINT chk_close_positive
    CHECK (close > 0);
ALTER TABLE price_history ADD CONSTRAINT chk_price_source
    CHECK (source IN ('yahoo_finance', 'alpha_vantage', 'coingecko', 'manual', 'import'));
```

**Price Sources:**
- `yahoo_finance`: Yahoo Finance API
- `alpha_vantage`: Alpha Vantage API
- `coingecko`: CoinGecko API (crypto)
- `manual`: Manually entered
- `import`: Imported from file

---

### 6. Portfolio Performance Cache Table

Cached performance metrics for fast retrieval.

```sql
CREATE TABLE portfolio_performance_cache (
    id BIGSERIAL PRIMARY KEY,
    portfolio_id BIGINT NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_value DECIMAL(15, 2) NOT NULL,
    total_cost_basis DECIMAL(15, 2) NOT NULL,
    total_gain_loss DECIMAL(15, 2),
    total_gain_loss_percent DECIMAL(10, 4),
    daily_return DECIMAL(10, 4),
    dividends_received DECIMAL(15, 2) DEFAULT 0,
    fees_paid DECIMAL(15, 2) DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(portfolio_id, date)
);

-- Indexes
CREATE INDEX idx_portfolio_performance_cache_portfolio_id ON portfolio_performance_cache(portfolio_id);
CREATE INDEX idx_portfolio_performance_cache_date ON portfolio_performance_cache(date DESC);
CREATE INDEX idx_portfolio_performance_cache_portfolio_date ON portfolio_performance_cache(portfolio_id, date DESC);
```

---

### 7. Benchmarks Table

Market benchmarks for comparison (S&P 500, etc.).

```sql
CREATE TABLE benchmarks (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    symbol VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    asset_id BIGINT REFERENCES assets(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_benchmarks_symbol ON benchmarks(symbol);
CREATE INDEX idx_benchmarks_is_active ON benchmarks(is_active);
```

---

### 8. Portfolio Benchmarks Table

Link portfolios to benchmarks for comparison.

```sql
CREATE TABLE portfolio_benchmarks (
    id BIGSERIAL PRIMARY KEY,
    portfolio_id BIGINT NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    benchmark_id BIGINT NOT NULL REFERENCES benchmarks(id) ON DELETE CASCADE,
    weight DECIMAL(5, 2) DEFAULT 100.00,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(portfolio_id, benchmark_id)
);

-- Indexes
CREATE INDEX idx_portfolio_benchmarks_portfolio_id ON portfolio_benchmarks(portfolio_id);
CREATE INDEX idx_portfolio_benchmarks_benchmark_id ON portfolio_benchmarks(benchmark_id);

-- Constraints
ALTER TABLE portfolio_benchmarks ADD CONSTRAINT chk_weight_range
    CHECK (weight > 0 AND weight <= 100);
```

---

## Cross-Service Relationships

### User References

Both Budget Service and Portfolio Service reference users via `user_id`. The authoritative user data is maintained by the API Gateway/Auth Service.

**Implementation:**
- Services store only `user_id` (BIGINT)
- User details fetched via API Gateway when needed
- No foreign key constraints across service boundaries
- Eventual consistency for user deletions

---

## Database Indexes Summary

### Budget Service Indexes

| Table | Index Type | Columns | Purpose |
|-------|-----------|---------|---------|
| users | B-tree | email | Fast login lookups |
| users | B-tree | uuid | External API references |
| accounts | B-tree | user_id | User's accounts |
| accounts | B-tree | type | Filter by account type |
| transactions | B-tree | user_id, date | User transaction history |
| transactions | B-tree | account_id | Account transactions |
| transactions | GIN | tags | Tag-based filtering |
| transactions | GIN | Full-text | Search description/payee |
| categories | B-tree | user_id | User's categories |
| budgets | B-tree | user_id | User's budgets |
| budgets | B-tree | start_date | Date range queries |

### Portfolio Service Indexes

| Table | Index Type | Columns | Purpose |
|-------|-----------|---------|---------|
| portfolios | B-tree | user_id | User's portfolios |
| assets | B-tree | symbol | Asset lookup |
| assets | GIN | Full-text | Asset search |
| holdings | B-tree | portfolio_id | Portfolio holdings |
| portfolio_transactions | B-tree | portfolio_id, date | Transaction history |
| price_history | B-tree | asset_id, date | Price lookup |

---

## Constraints & Validation Rules

### Data Integrity Constraints

1. **Referential Integrity**
   - All foreign keys with appropriate CASCADE rules
   - ON DELETE CASCADE: Delete child records with parent
   - ON DELETE SET NULL: Preserve child records, nullify reference

2. **Check Constraints**
   - Enum validation for type fields
   - Positive amounts for transactions/budgets
   - Date range validation
   - Email format validation
   - Currency code format (ISO 4217)

3. **Unique Constraints**
   - Prevent duplicate user emails
   - Prevent duplicate portfolio/asset combinations
   - Prevent duplicate budget periods

### Application-Level Validations

**SQLAlchemy Models should enforce:**
- Required fields
- String length limits
- Numeric precision
- Relationship validations
- Custom business logic

**Example validations:**
```python
# Pydantic schema example
class TransactionCreate(BaseModel):
    amount: condecimal(gt=0, decimal_places=2)
    date: date
    description: constr(min_length=1, max_length=1000)
    type: Literal['income', 'expense', 'transfer']

    @validator('date')
    def date_not_future(cls, v):
        if v > date.today():
            raise ValueError('Transaction date cannot be in the future')
        return v
```

---

## Performance Optimization

### Query Optimization

1. **Composite Indexes**
   - `(user_id, date)` for transaction queries
   - `(portfolio_id, asset_id)` for holdings
   - `(asset_id, date)` for price history

2. **Partial Indexes**
   - Index only active records: `WHERE deleted_at IS NULL`
   - Index only positive quantities: `WHERE quantity > 0`

3. **Covering Indexes**
   - Include frequently accessed columns in index

### Caching Strategy

1. **Budget Spending Cache**
   - Pre-calculated spending totals per budget period
   - Updated on transaction create/update/delete
   - Invalidated on budget changes

2. **Portfolio Performance Cache**
   - Daily portfolio snapshots
   - Calculated by Celery task
   - Enables fast historical performance queries

3. **Application-Level Caching**
   - Redis caching for:
     - User preferences
     - Category lists
     - Current prices
     - Exchange rates

### Database Partitioning (Future)

For large datasets, consider partitioning:
- **Transactions**: Partition by date (monthly/yearly)
- **Price History**: Partition by date (yearly)
- **Portfolio Transactions**: Partition by date (yearly)

---

## Migration Strategy

### Alembic Migration Plan

**Phase 1: Core Tables**
1. Users, Accounts, Categories
2. Transactions
3. Budgets, Recurring Transactions

**Phase 2: Portfolio Tables**
1. Portfolios, Assets
2. Holdings, Portfolio Transactions
3. Price History

**Phase 3: Optimization**
1. Cache tables
2. Additional indexes
3. Performance tuning

### Migration Template

```python
"""Create users and accounts tables

Revision ID: 001
Revises:
Create Date: 2025-11-12
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        # ... other columns
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('uuid')
    )

    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade():
    op.drop_index('idx_users_email')
    op.drop_table('users')
```

---

## Security Considerations

### Data Protection

1. **Sensitive Data**
   - Password hashes: Use bcrypt/argon2
   - Account numbers: Consider encryption at rest
   - Personal data: GDPR compliance

2. **Row-Level Security (RLS)**
   - Optional: PostgreSQL RLS for multi-tenancy
   - Ensure users can only access their own data

3. **Audit Trail**
   - Soft deletes preserve data
   - `created_at`/`updated_at` timestamps
   - Consider audit log table for critical operations

### Access Control

- Database users with minimal privileges
- Separate read-only user for analytics
- Connection pooling with timeout
- SSL/TLS for database connections

---

## Backup & Recovery

### Backup Strategy

1. **Automated Backups**
   - Daily full backups
   - Hourly incremental backups
   - Point-in-time recovery enabled

2. **Retention Policy**
   - Daily backups: 30 days
   - Weekly backups: 12 weeks
   - Monthly backups: 12 months

3. **Testing**
   - Monthly restore tests
   - Documented recovery procedures

---

## Monitoring & Maintenance

### Database Monitoring

1. **Metrics to Track**
   - Query performance (slow queries)
   - Connection pool usage
   - Table sizes and growth
   - Index usage statistics
   - Cache hit ratios

2. **Alerts**
   - Slow queries (> 1 second)
   - High connection count
   - Database size approaching limit
   - Failed backups

### Maintenance Tasks

1. **Regular Tasks**
   - `VACUUM ANALYZE` weekly
   - Reindex fragmented indexes
   - Update table statistics
   - Check for unused indexes

2. **Monitoring Queries**
```sql
-- Find slow queries
SELECT * FROM pg_stat_statements
ORDER BY mean_exec_time DESC LIMIT 10;

-- Find unused indexes
SELECT * FROM pg_stat_user_indexes
WHERE idx_scan = 0;

-- Table sizes
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## Future Enhancements

### Planned Improvements

1. **Time-Series Data**
   - Consider TimescaleDB extension for price_history
   - Better compression and query performance

2. **Full-Text Search**
   - PostgreSQL full-text search for transactions
   - Consider Elasticsearch for advanced search

3. **Materialized Views**
   - Portfolio performance summaries
   - Budget vs. spending reports
   - Asset allocation breakdowns

4. **Event Sourcing**
   - Append-only event log
   - Rebuild state from events
   - Complete audit trail

---

## Appendix

### Database Size Estimates

**1,000 users, 1 year of data:**

| Table | Rows | Size |
|-------|------|------|
| users | 1,000 | 200 KB |
| accounts | 5,000 | 1 MB |
| categories | 10,000 | 2 MB |
| transactions | 500,000 | 150 MB |
| budgets | 20,000 | 5 MB |
| portfolios | 3,000 | 1 MB |
| holdings | 15,000 | 5 MB |
| portfolio_transactions | 100,000 | 30 MB |
| price_history | 1,000,000 | 200 MB |
| **Total** | | **~600 MB** |

### Useful Commands

```sql
-- Create database
CREATE DATABASE budget_db;
CREATE DATABASE portfolio_db;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy search

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE budget_db TO fincloud_user;
GRANT ALL PRIVILEGES ON DATABASE portfolio_db TO fincloud_user;
```

---

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/14/orm/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [Database Design Best Practices](https://www.postgresql.org/docs/current/ddl.html)
- [ISO 4217 Currency Codes](https://www.iso.org/iso-4217-currency-codes.html)

---

**Document Version**: 1.0
**Last Review**: 2025-11-12
**Next Review**: 2025-12-12
