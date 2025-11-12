# FinCloud Database ERD

**Status**: Schema Designed ✅
**Generated Diagrams**: Run `./docs/architecture/generate-erd.sh` to create PNG files

## Quick Links

- **[Complete Database Schema](./database-schema.md)** - Full technical specification
- **[Mermaid Diagrams](./erd-diagram.md)** - Interactive diagrams (renders in GitHub/GitLab)
- **[ERD Setup Guide](./ERD-README.md)** - How to generate PNG diagrams

## Database Overview

FinCloud uses PostgreSQL with a schema-per-service architecture:

### Budget Service (8 tables)
- **users** - User accounts and authentication
- **accounts** - Financial accounts (checking, savings, credit cards, etc.)
- **categories** - Transaction categories with hierarchical support
- **transactions** - Financial transactions (income, expense, transfers)
- **budgets** - Budget allocations and tracking
- **recurring_transactions** - Recurring transaction templates
- **tags** - Reusable transaction tags
- **budget_spending_cache** - Performance optimization cache

### Portfolio Service (8 tables)
- **portfolios** - Investment portfolios
- **assets** - Investment assets (stocks, ETFs, crypto, bonds)
- **holdings** - Current portfolio positions
- **portfolio_transactions** - Buy/sell/dividend transactions
- **price_history** - Historical price data
- **portfolio_performance_cache** - Performance metrics cache
- **benchmarks** - Market benchmarks (S&P 500, etc.)
- **portfolio_benchmarks** - Portfolio-benchmark associations

## Key Design Decisions

### 1. Schema-per-Service
- Each microservice has its own PostgreSQL database
- Better isolation, independent scaling
- User references via `user_id` (no cross-service FKs)

### 2. Soft Deletes
- All tables include `deleted_at` timestamp
- Enables audit trail and data recovery
- Queries filter `WHERE deleted_at IS NULL`

### 3. UUIDs for External APIs
- Internal: BIGINT/SERIAL primary keys (performance)
- External: UUID for API responses (security, decoupling)

### 4. Strategic Denormalization
- Cache tables for performance-critical queries
- Pre-calculated budget spending totals
- Pre-calculated portfolio performance metrics

### 5. Performance Optimizations
- Composite indexes on common query patterns
- Partial indexes for active records only
- GIN indexes for full-text search and array fields
- Strategic use of JSONB for flexible metadata

## Entity Relationships Summary

### Budget Service Core Flow
```
User → Accounts → Transactions ← Categories
                            ↓
                          Budgets
```

### Portfolio Service Core Flow
```
User → Portfolios → Holdings ← Assets
              ↓                   ↓
   Portfolio Transactions    Price History
```

## Viewing the ERD

### Option 1: GitHub Markdown (Easiest)
View the Mermaid diagrams directly in [erd-diagram.md](./erd-diagram.md) - they render automatically on GitHub.

### Option 2: Generate PNG Files
```bash
./docs/architecture/generate-erd.sh
```

### Option 3: Online Viewer
1. Visit https://mermaid.live/
2. Copy diagram from [erd-diagram.md](./erd-diagram.md)
3. Export as PNG/SVG

## Next Steps

After reviewing the schema:

1. **Implement SQLAlchemy Models** (see database-schema.md for field definitions)
2. **Create Alembic Migrations** (schema versioning)
3. **Add Model Validations** (Pydantic schemas)
4. **Write Unit Tests** (model validation and relationships)
5. **Performance Testing** (ensure indexes are effective)

## Resources

- [Full Schema Documentation](./database-schema.md)
- [SQLAlchemy Best Practices](https://docs.sqlalchemy.org/en/14/orm/relationships.html)
- [PostgreSQL Performance Tips](https://www.postgresql.org/docs/current/performance-tips.html)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

---

**Last Updated**: 2025-11-12
**Schema Version**: 1.0
