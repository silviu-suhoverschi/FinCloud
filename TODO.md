# FinCloud - Development TODO

> Last Updated: 2025-11-13
> Current Phase: **Phase 0 - Project Setup** ✅ COMPLETED
> Next Phase: **Phase 1 - MVP Development**

## Legend

- ✅ Completed
- 🚧 In Progress
- 📋 Planned
- 🔴 Blocked
- 💡 Enhancement/Optional

---

## Phase 0: Project Setup ✅ COMPLETED

### Repository & Infrastructure ✅
- ✅ Create mono-repo directory structure
- ✅ Set up .gitignore, LICENSE, CONTRIBUTING.md
- ✅ Create README.md with project overview
- ✅ Set up environment configuration (.env.example)
- ✅ Create Makefile for common operations

### Backend Services ✅
- ✅ Budget Service skeleton (FastAPI + SQLAlchemy)
- ✅ Portfolio Service skeleton (FastAPI + Celery)
- ✅ API Gateway placeholder
- ✅ Notification Service placeholder
- ✅ Docker Compose configuration
- ✅ Database initialization scripts

### Frontend ✅
- ✅ Next.js 14 project structure
- ✅ TypeScript configuration
- ✅ Tailwind CSS setup
- ✅ Basic landing page
- ✅ Docker configuration (dev & prod)

### DevOps ✅
- ✅ GitHub Actions CI pipeline
- ✅ GitHub Actions release workflow
- ✅ GitHub Actions deployment workflow
- ✅ Helm chart structure
- ✅ Kubernetes manifests

### Documentation ✅
- ✅ MkDocs setup with Material theme
- ✅ Architecture overview
- ✅ Quick start guide
- ✅ Installation guide

---

## Phase 1: MVP Development (Target: 3 months)

### 1.1 Database & Models 📋

#### Budget Service Database
- ✅ Design database schema (ERD)
- ✅ Create SQLAlchemy models:
  - ✅ User model (id, email, password_hash, created_at)
  - ✅ Account model (id, user_id, name, type, currency, balance)
  - ✅ Category model (id, user_id, name, type, parent_id)
  - ✅ Transaction model (id, account_id, category_id, amount, date, description)
  - ✅ Budget model (id, user_id, category_id, amount, period, start_date)
  - ✅ RecurringTransaction model
  - ✅ Tag model (additional)
  - ✅ BudgetSpendingCache model (additional)
- ✅ Create Alembic migrations
- ✅ Add database indexes for performance
- ✅ Write model validators and constraints

#### Portfolio Service Database
- ✅ Design portfolio database schema
- ✅ Create SQLAlchemy models:
  - ✅ Portfolio model (id, user_id, name, description)
  - ✅ Asset model (id, symbol, name, type, exchange)
  - ✅ Holding model (id, portfolio_id, asset_id, quantity)
  - ✅ PortfolioTransaction model (buy/sell/dividend)
  - ✅ PriceHistory model (asset_id, date, price, source)
  - ✅ PortfolioPerformanceCache model (additional)
  - ✅ Benchmark model (additional)
  - ✅ PortfolioBenchmark model (additional)
- ✅ Create Alembic migrations
- ✅ Add composite indexes for queries

### 1.2 Authentication & Authorization ✅

- ✅ Implement JWT token generation
- ✅ Create password hashing utilities (bcrypt)
- ✅ Build user registration endpoint
- ✅ Build login endpoint
- ✅ Build token refresh endpoint
- ✅ Add authentication middleware
- ✅ Implement RBAC (Role-Based Access Control)
- ✅ Add user profile endpoints
- ✅ Password reset functionality
- ✅ Email verification (optional for MVP)

### 1.3 Budget Service Implementation 📋

#### Account Management ✅
- ✅ GET /api/v1/accounts - List accounts
- ✅ POST /api/v1/accounts - Create account
- ✅ GET /api/v1/accounts/{id} - Get account details
- ✅ PUT /api/v1/accounts/{id} - Update account
- ✅ DELETE /api/v1/accounts/{id} - Delete account
- ✅ GET /api/v1/accounts/{id}/balance - Get account balance

#### Transaction Management ✅
- ✅ GET /api/v1/transactions - List transactions (with filters)
- ✅ POST /api/v1/transactions - Create transaction
- ✅ GET /api/v1/transactions/{id} - Get transaction
- ✅ PUT /api/v1/transactions/{id} - Update transaction
- ✅ DELETE /api/v1/transactions/{id} - Delete transaction
- ✅ POST /api/v1/transactions/bulk - Bulk import (CSV)
- ✅ GET /api/v1/transactions/search - Full-text search

#### Category Management
- ✅ GET /api/v1/categories - List categories
- ✅ POST /api/v1/categories - Create category
- ✅ PUT /api/v1/categories/{id} - Update category
- ✅ DELETE /api/v1/categories/{id} - Delete category
- ✅ Implement category hierarchies (parent/child)
- ✅ GET /api/v1/categories/tree - Get hierarchical category tree
- ✅ GET /api/v1/categories/{id}/usage - Get category usage statistics

#### Budget Management
- 📋 GET /api/v1/budgets - List budgets
- 📋 POST /api/v1/budgets - Create budget
- 📋 GET /api/v1/budgets/{id} - Get budget with spending
- 📋 PUT /api/v1/budgets/{id} - Update budget
- 📋 DELETE /api/v1/budgets/{id} - Delete budget
- 📋 GET /api/v1/budgets/{id}/progress - Budget progress

#### Reports & Analytics
- 📋 GET /api/v1/reports/cashflow - Monthly cashflow
- 📋 GET /api/v1/reports/spending - Spending by category
- 📋 GET /api/v1/reports/income - Income analysis
- 📋 GET /api/v1/reports/net-worth - Net worth timeline

### 1.4 Portfolio Service Implementation 📋

#### Portfolio Management
- 📋 GET /api/v1/portfolios - List portfolios
- 📋 POST /api/v1/portfolios - Create portfolio
- 📋 GET /api/v1/portfolios/{id} - Get portfolio details
- 📋 PUT /api/v1/portfolios/{id} - Update portfolio
- 📋 DELETE /api/v1/portfolios/{id} - Delete portfolio

#### Holdings Management
- 📋 GET /api/v1/holdings - List all holdings
- 📋 POST /api/v1/holdings - Add holding
- 📋 GET /api/v1/holdings/{id} - Get holding details
- 📋 PUT /api/v1/holdings/{id} - Update holding
- 📋 DELETE /api/v1/holdings/{id} - Remove holding

#### Transaction Management
- 📋 GET /api/v1/transactions - List portfolio transactions
- 📋 POST /api/v1/transactions - Record transaction
- 📋 Support transaction types: BUY, SELL, DIVIDEND, SPLIT

#### Price Fetching
- 📋 Implement Yahoo Finance integration
- 📋 Implement Alpha Vantage integration
- 📋 Implement CoinGecko integration (crypto)
- 📋 Create Celery task for price updates
- 📋 Schedule hourly price refreshes
- 📋 Handle API rate limits and retries
- 📋 Cache price data in Redis

#### Analytics & Performance
- 📋 Calculate portfolio total value
- 📋 Calculate ROI (Return on Investment)
- 📋 Calculate XIRR (Extended Internal Rate of Return)
- 📋 Calculate TWR (Time-Weighted Return)
- 📋 Asset allocation breakdown
- 📋 Gain/loss per holding
- 📋 Dividend tracking and yield

### 1.5 API Gateway 📋

- 📋 Set up FastAPI application
- 📋 Implement request routing to services
- 📋 Add authentication middleware
- 📋 Configure CORS properly
- 📋 Add rate limiting (Redis-based)
- 📋 Aggregate service health checks
- 📋 Create unified OpenAPI documentation
- 📋 Add request/response logging
- 📋 Implement circuit breaker pattern

### 1.6 Notification Service 📋

- 📋 Set up FastAPI application
- 📋 Implement email notifications (SMTP)
- 📋 Implement Telegram notifications
- 📋 Create notification templates
- 📋 Build webhook dispatcher
- 📋 Add event queue (Redis)
- 📋 Create notification preferences endpoint

### 1.7 Frontend Development 📋

#### Layout & Navigation
- 📋 Create app layout with sidebar
- 📋 Build navigation menu
- 📋 Add user profile dropdown
- 📋 Implement responsive mobile menu
- 📋 Add dark/light theme toggle

#### Authentication Pages
- 📋 Login page with form validation
- 📋 Registration page
- 📋 Password reset page
- 📋 Email verification page

#### Dashboard
- 📋 Overview dashboard with key metrics
- 📋 Recent transactions widget
- 📋 Budget summary widget
- 📋 Portfolio value chart
- 📋 Net worth timeline chart

#### Budget Module
- 📋 Accounts list page
- 📋 Account detail page
- 📋 Transaction list with filters
- 📋 Transaction create/edit form
- 📋 Category management page
- 📋 Budget list page
- 📋 Budget create/edit form
- 📋 Budget progress visualization

#### Portfolio Module
- 📋 Portfolio list page
- 📋 Portfolio detail page with charts
- 📋 Holdings table
- 📋 Add holding form
- 📋 Transaction history
- 📋 Performance charts (ROI, allocation)
- 📋 Asset search/autocomplete

#### Reports
- 📋 Cashflow report with charts
- 📋 Spending by category (pie chart)
- 📋 Income vs expenses timeline
- 📋 Net worth chart
- 📋 Export reports (PDF/CSV)

#### Settings
- 📋 User profile settings
- 📋 Notification preferences
- 📋 Currency settings
- 📋 Theme preferences
- 📋 API keys management

### 1.8 Testing 📋

#### Backend Tests
- 📋 Budget Service unit tests (80%+ coverage)
- 📋 Portfolio Service unit tests (80%+ coverage)
- 📋 API Gateway tests
- 📋 Integration tests for critical flows
- 📋 API endpoint tests

#### Frontend Tests
- 📋 Component unit tests (Jest + Testing Library)
- 📋 Integration tests for key flows
- 📋 E2E tests (Playwright/Cypress)

### 1.9 Documentation 📋

- 📋 API Reference documentation
- 📋 User guide for budget management
- 📋 User guide for portfolio tracking
- 📋 Developer setup guide
- 📋 Deployment guide
- 📋 Screenshots and video demos

### 1.10 DevOps & Deployment 📋

- 📋 Set up container registry (GHCR)
- 📋 Configure production environment variables
- 📋 Set up PostgreSQL backup strategy
- 📋 Configure monitoring (Prometheus)
- 📋 Set up logging (Loki)
- 📋 Create Grafana dashboards
- 📋 Set up alerts for critical issues
- 📋 SSL/TLS certificates (Let's Encrypt)

---

## Phase 2: Integrations (Target: 2 months after MVP)

### 2.1 GraphQL API 💡
- 📋 Set up Strawberry GraphQL
- 📋 Define GraphQL schema
- 📋 Implement resolvers
- 📋 Add subscriptions for real-time updates
- 📋 GraphQL playground

### 2.2 Webhooks 💡
- 📋 Webhook registration endpoint
- 📋 Event triggering system
- 📋 Webhook retry logic
- 📋 Webhook security (signing)

### 2.3 n8n Integration 💡
- 📋 Create n8n node package
- 📋 Implement triggers (new transaction, budget alert)
- 📋 Implement actions (create transaction, etc.)
- 📋 Documentation and examples

### 2.4 Home Assistant Integration 💡
- 📋 Create HACS component
- 📋 Expose sensors (account balance, portfolio value)
- 📋 Create services (add transaction)
- 📋 Integration documentation

### 2.5 Mobile PWA Enhancements 💡
- 📋 Add service worker for offline support
- 📋 Implement push notifications
- 📋 Add to home screen prompt
- 📋 Optimize mobile performance

---

## Phase 3: AI & Plugins (Target: 4 months)

### 3.1 Plugin Framework 💡
- 📋 Design plugin architecture
- 📋 Create plugin SDK
- 📋 Plugin registration system
- 📋 Plugin marketplace backend
- 📋 Plugin security sandboxing

### 3.2 AI Features 💡
- 📋 Transaction categorization ML model
- 📋 Spending prediction
- 📋 Budget recommendations
- 📋 Anomaly detection
- 📋 Investment insights

### 3.3 Example Plugins 💡
- 📋 Romanian Tax Helper plugin
- 📋 Energy Asset Tracker plugin
- 📋 Receipt OCR plugin

---

## Phase 4: Mobile & Polish (Target: 2 months)

### 4.1 Mobile Optimization 💡
- 📋 Performance optimization
- 📋 Touch gesture support
- 📋 Mobile-first components
- 📋 Camera integration (receipt scan)

### 4.2 UI/UX Polish 💡
- 📋 Animations and transitions
- 📋 Loading states
- 📋 Error handling UX
- 📋 Accessibility (WCAG 2.1)
- 📋 Internationalization (i18n)

### 4.3 Advanced Features 💡
- 📋 Multi-currency support
- 📋 Split transactions
- 📋 Recurring transaction templates
- 📋 Goals and savings targets
- 📋 Debt tracking
- 📋 Subscription tracking

---

## Immediate Next Steps (This Week)

1. **Database Schema Design**
   - Create ERD for budget and portfolio databases
   - Define all relationships and constraints
   - Review and validate schema

2. **Authentication Implementation**
   - Set up JWT utilities
   - Create User model
   - Implement registration and login endpoints
   - Add authentication middleware

3. **Budget Service - Core Endpoints**
   - Implement Account CRUD
   - Implement Transaction CRUD
   - Add basic validation

4. **Frontend - Authentication Flow**
   - Build login/registration pages
   - Implement API client
   - Add authentication state management

5. **Testing Setup**
   - Configure pytest for services
   - Configure Jest for frontend
   - Write first test cases

---

## Blockers & Dependencies

### Current Blockers
- 🔴 None

### External Dependencies
- Alpha Vantage API key (for stock prices)
- CoinGecko API key (for crypto prices)
- SMTP server for email notifications
- Telegram bot token (optional)

---

## Notes

- Focus on MVP features first
- Prioritize user experience
- Write tests as you develop
- Document as you build
- Regular commits and PRs
- Weekly progress reviews

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Alpha Vantage API](https://www.alphavantage.co/documentation/)
- [Yahoo Finance API](https://pypi.org/project/yfinance/)
