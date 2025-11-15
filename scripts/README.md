# FinCloud Scripts

This directory contains utility scripts for managing the FinCloud application.

## Migration Scripts

### run-migrations.sh

Applies all pending database migrations to the FinCloud services.

**Usage:**

```bash
# Make sure services are running first
make dev

# Run migrations
./scripts/run-migrations.sh

# Or use the Makefile target
make migrate
```

**What it does:**
- Runs Alembic migrations for the Budget Service
- Runs Alembic migrations for the Portfolio Service
- Verifies that migrations complete successfully

**Prerequisites:**
- Docker and docker-compose must be installed
- Services must be running (`docker-compose up -d` or `make dev`)

### Running Individual Service Migrations

If you need to run migrations for a specific service:

```bash
# Budget Service only
make migrate-budget
# or
docker-compose exec budget-service alembic upgrade head

# Portfolio Service only
make migrate-portfolio
# or
docker-compose exec portfolio-service alembic upgrade head
```

## Troubleshooting

### Migration Chain Errors

If you see errors about missing revisions or broken migration chains:

1. Check that all migration files exist in `services/<service>/alembic/versions/`
2. Verify that each migration's `down_revision` points to an existing migration
3. Check the current database version:
   ```bash
   docker-compose exec budget-service alembic current
   ```

### Database Connection Issues

If migrations fail with database connection errors:

1. Verify PostgreSQL is running: `docker-compose ps postgres`
2. Check database logs: `docker-compose logs postgres`
3. Ensure the database is healthy: `docker-compose exec postgres pg_isready -U fincloud`
