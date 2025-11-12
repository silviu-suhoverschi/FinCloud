# Entity Relationship Diagrams (ERD)

This document contains the ERD for FinCloud's database schema using Mermaid diagram syntax.

## How to Generate PNG

### Method 1: Using Mermaid CLI

```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Generate Budget Service ERD
mmdc -i docs/architecture/erd-diagram.md -o docs/architecture/erd-budget-service.png -b transparent

# Generate Portfolio Service ERD
mmdc -i docs/architecture/erd-diagram.md -o docs/architecture/erd-portfolio-service.png -b transparent
```

### Method 2: Using Online Tools

1. Visit [Mermaid Live Editor](https://mermaid.live/)
2. Copy the Mermaid code below
3. Export as PNG/SVG

### Method 3: Using draw.io

1. Visit [draw.io](https://app.diagrams.net/)
2. Import the database schema from the markdown file
3. Use the database import feature or create manually
4. Export as PNG

---

## Budget Service ERD

```mermaid
erDiagram
    USERS ||--o{ ACCOUNTS : owns
    USERS ||--o{ CATEGORIES : creates
    USERS ||--o{ TRANSACTIONS : creates
    USERS ||--o{ BUDGETS : creates
    USERS ||--o{ RECURRING_TRANSACTIONS : creates
    USERS ||--o{ TAGS : creates

    ACCOUNTS ||--o{ TRANSACTIONS : "source account"
    ACCOUNTS ||--o{ TRANSACTIONS : "destination account"
    ACCOUNTS ||--o{ RECURRING_TRANSACTIONS : "source account"
    ACCOUNTS ||--o{ BUDGETS : "scoped to"

    CATEGORIES ||--o{ CATEGORIES : "parent/child"
    CATEGORIES ||--o{ TRANSACTIONS : categorizes
    CATEGORIES ||--o{ BUDGETS : "scoped to"
    CATEGORIES ||--o{ RECURRING_TRANSACTIONS : categorizes

    BUDGETS ||--o{ BUDGET_SPENDING_CACHE : "cached spending"

    RECURRING_TRANSACTIONS ||--o{ TRANSACTIONS : generates

    USERS {
        bigint id PK
        uuid uuid UK
        varchar email UK
        varchar password_hash
        varchar first_name
        varchar last_name
        boolean is_active
        boolean is_verified
        timestamp email_verified_at
        timestamp last_login_at
        varchar preferred_currency
        varchar timezone
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at
    }

    ACCOUNTS {
        bigint id PK
        uuid uuid UK
        bigint user_id FK
        varchar name
        varchar type
        varchar currency
        decimal initial_balance
        decimal current_balance
        varchar account_number
        varchar institution
        varchar color
        varchar icon
        boolean is_active
        boolean include_in_net_worth
        text notes
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at
    }

    CATEGORIES {
        bigint id PK
        uuid uuid UK
        bigint user_id FK
        bigint parent_id FK
        varchar name
        varchar type
        varchar color
        varchar icon
        boolean is_active
        integer sort_order
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at
    }

    TRANSACTIONS {
        bigint id PK
        uuid uuid UK
        bigint user_id FK
        bigint account_id FK
        bigint category_id FK
        bigint destination_account_id FK
        varchar type
        decimal amount
        varchar currency
        decimal exchange_rate
        date date
        text description
        varchar payee
        varchar reference_number
        text notes
        text[] tags
        boolean is_reconciled
        timestamp reconciled_at
        bigint recurring_transaction_id FK
        varchar external_id
        varchar import_source
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at
    }

    BUDGETS {
        bigint id PK
        uuid uuid UK
        bigint user_id FK
        bigint category_id FK
        bigint account_id FK
        varchar name
        decimal amount
        varchar currency
        varchar period
        date start_date
        date end_date
        boolean rollover_unused
        boolean alert_enabled
        decimal alert_threshold
        boolean is_active
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at
    }

    RECURRING_TRANSACTIONS {
        bigint id PK
        uuid uuid UK
        bigint user_id FK
        bigint account_id FK
        bigint category_id FK
        bigint destination_account_id FK
        varchar type
        decimal amount
        varchar currency
        text description
        varchar payee
        varchar frequency
        integer interval_count
        date start_date
        date end_date
        date next_occurrence
        timestamp last_generated_at
        integer occurrences_count
        integer max_occurrences
        boolean is_active
        boolean auto_create
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at
    }

    TAGS {
        bigint id PK
        bigint user_id FK
        varchar name
        varchar color
        integer usage_count
        timestamp created_at
        timestamp updated_at
    }

    BUDGET_SPENDING_CACHE {
        bigint id PK
        bigint budget_id FK
        date period_start
        date period_end
        decimal total_spent
        decimal total_budget
        integer transaction_count
        timestamp last_calculated_at
    }
```

---

## Portfolio Service ERD

```mermaid
erDiagram
    PORTFOLIOS ||--o{ HOLDINGS : contains
    PORTFOLIOS ||--o{ PORTFOLIO_TRANSACTIONS : "has transactions"
    PORTFOLIOS ||--o{ PORTFOLIO_PERFORMANCE_CACHE : "performance cache"
    PORTFOLIOS ||--o{ PORTFOLIO_BENCHMARKS : "compared to"

    ASSETS ||--o{ HOLDINGS : "held in"
    ASSETS ||--o{ PORTFOLIO_TRANSACTIONS : "traded"
    ASSETS ||--o{ PRICE_HISTORY : "price data"
    ASSETS ||--o{ BENCHMARKS : "benchmark asset"

    BENCHMARKS ||--o{ PORTFOLIO_BENCHMARKS : "benchmark for"

    PORTFOLIOS {
        bigint id PK
        uuid uuid UK
        bigint user_id
        varchar name
        text description
        varchar currency
        boolean is_active
        integer sort_order
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at
    }

    ASSETS {
        bigint id PK
        uuid uuid UK
        varchar symbol
        varchar name
        varchar type
        varchar asset_class
        varchar sector
        varchar exchange
        varchar currency
        varchar isin
        varchar cusip
        varchar figi
        varchar country
        text logo_url
        boolean is_active
        jsonb metadata
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at
    }

    HOLDINGS {
        bigint id PK
        uuid uuid UK
        bigint portfolio_id FK
        bigint asset_id FK
        decimal quantity
        decimal average_cost
        decimal cost_basis
        decimal current_price
        decimal current_value
        decimal unrealized_gain_loss
        decimal unrealized_gain_loss_percent
        timestamp last_price_update
        text notes
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at
    }

    PORTFOLIO_TRANSACTIONS {
        bigint id PK
        uuid uuid UK
        bigint portfolio_id FK
        bigint asset_id FK
        varchar type
        decimal quantity
        decimal price
        decimal total_amount
        decimal fee
        decimal tax
        varchar currency
        decimal exchange_rate
        date date
        text notes
        varchar reference_number
        varchar external_id
        varchar import_source
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at
    }

    PRICE_HISTORY {
        bigint id PK
        bigint asset_id FK
        date date
        decimal open
        decimal high
        decimal low
        decimal close
        decimal adjusted_close
        bigint volume
        varchar source
        timestamp created_at
    }

    PORTFOLIO_PERFORMANCE_CACHE {
        bigint id PK
        bigint portfolio_id FK
        date date
        decimal total_value
        decimal total_cost_basis
        decimal total_gain_loss
        decimal total_gain_loss_percent
        decimal daily_return
        decimal dividends_received
        decimal fees_paid
        timestamp created_at
    }

    BENCHMARKS {
        bigint id PK
        uuid uuid UK
        varchar symbol UK
        varchar name
        text description
        bigint asset_id FK
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    PORTFOLIO_BENCHMARKS {
        bigint id PK
        bigint portfolio_id FK
        bigint benchmark_id FK
        decimal weight
        timestamp created_at
    }
```

---

## Complete System ERD (Simplified)

This diagram shows the high-level relationships between Budget and Portfolio services.

```mermaid
erDiagram
    USERS ||--o{ ACCOUNTS : "budget service"
    USERS ||--o{ TRANSACTIONS : "budget service"
    USERS ||--o{ BUDGETS : "budget service"
    USERS ||--o{ PORTFOLIOS : "portfolio service"

    ACCOUNTS ||--o{ TRANSACTIONS : has
    TRANSACTIONS }o--|| CATEGORIES : categorized_by
    BUDGETS }o--|| CATEGORIES : scoped_to

    PORTFOLIOS ||--o{ HOLDINGS : contains
    HOLDINGS }o--|| ASSETS : "asset type"
    PORTFOLIOS ||--o{ PORTFOLIO_TRANSACTIONS : has
    PORTFOLIO_TRANSACTIONS }o--|| ASSETS : trades

    ASSETS ||--o{ PRICE_HISTORY : "price data"

    USERS {
        bigint id PK
        varchar email
        varchar name
    }

    ACCOUNTS {
        bigint id PK
        varchar name
        varchar type
        decimal balance
    }

    TRANSACTIONS {
        bigint id PK
        decimal amount
        date date
        varchar type
    }

    BUDGETS {
        bigint id PK
        decimal amount
        varchar period
    }

    CATEGORIES {
        bigint id PK
        varchar name
        varchar type
    }

    PORTFOLIOS {
        bigint id PK
        varchar name
        varchar currency
    }

    ASSETS {
        bigint id PK
        varchar symbol
        varchar name
        varchar type
    }

    HOLDINGS {
        bigint id PK
        decimal quantity
        decimal value
    }

    PORTFOLIO_TRANSACTIONS {
        bigint id PK
        varchar type
        decimal quantity
        decimal price
    }

    PRICE_HISTORY {
        bigint id PK
        date date
        decimal close
    }
```

---

## Database Schema Visual Summary

### Budget Service Tables (8 tables)

1. **users** - User accounts and authentication
2. **accounts** - Financial accounts (bank, credit, etc.)
3. **categories** - Transaction categories (hierarchical)
4. **transactions** - Financial transactions
5. **budgets** - Budget allocations
6. **recurring_transactions** - Recurring transaction templates
7. **tags** - Reusable tags
8. **budget_spending_cache** - Performance cache

### Portfolio Service Tables (8 tables)

1. **portfolios** - Investment portfolios
2. **assets** - Investment assets (stocks, crypto, etc.)
3. **holdings** - Current positions
4. **portfolio_transactions** - Buy/sell transactions
5. **price_history** - Historical prices
6. **portfolio_performance_cache** - Performance metrics cache
7. **benchmarks** - Market benchmarks
8. **portfolio_benchmarks** - Portfolio-benchmark relationships

### Key Relationships

**Budget Service:**
- One user → Many accounts
- One account → Many transactions
- One category → Many transactions (and subcategories)
- One budget → One category/account
- One recurring transaction → Many generated transactions

**Portfolio Service:**
- One user → Many portfolios
- One portfolio → Many holdings
- One asset → Many holdings (across portfolios)
- One portfolio → Many transactions
- One asset → Many price history records

---

## Converting to PNG

### Using Mermaid CLI (Recommended)

```bash
# Install dependencies
npm install -g @mermaid-js/mermaid-cli

# Generate Budget Service ERD
echo '```mermaid' > budget-erd.mmd
# Copy the Budget Service ERD from above
echo '```' >> budget-erd.mmd
mmdc -i budget-erd.mmd -o docs/architecture/erd-budget-service.png

# Generate Portfolio Service ERD
echo '```mermaid' > portfolio-erd.mmd
# Copy the Portfolio Service ERD from above
echo '```' >> portfolio-erd.mmd
mmdc -i portfolio-erd.mmd -o docs/architecture/erd-portfolio-service.png

# Generate Complete System ERD
echo '```mermaid' > system-erd.mmd
# Copy the Complete System ERD from above
echo '```' >> system-erd.mmd
mmdc -i system-erd.mmd -o docs/architecture/erd-system.png
```

### Manual Creation with draw.io

If you prefer a more visual tool:

1. Visit [draw.io](https://app.diagrams.net/)
2. Create a new diagram
3. Use the Entity Relation shape library
4. Refer to `database-schema.md` for all fields and relationships
5. Export as PNG with transparent background

**Recommended Layout:**
- Budget Service: Left side
- Portfolio Service: Right side
- Users table: Top center (shared reference)
- Use colors to differentiate:
  - Core tables: Blue
  - Cache tables: Green
  - Relationship tables: Yellow

---

## Notes

- All Mermaid diagrams above can be rendered in GitHub, GitLab, and many markdown viewers
- For production documentation, convert to PNG/SVG using one of the methods above
- The ERD shows logical relationships; physical implementation uses `user_id` references across services
- Cascade rules (ON DELETE CASCADE, SET NULL) are documented in `database-schema.md`

---

**Last Updated**: 2025-11-12
