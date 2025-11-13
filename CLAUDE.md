# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FinCloud is a self-hosted, privacy-first personal finance and investment management platform that combines budgeting (like Firefly III) with portfolio tracking (like Ghostfolio). It's built as a cloud-native microservices architecture using Python/FastAPI for the backend and React/Next.js for the frontend.

## Architecture

### Microservices Structure

The system consists of 5 main services that communicate through an API Gateway:

1. **API Gateway** (`services/api-gateway/`) - Port 8000
   - Entry point for all client requests
   - Handles authentication (JWT-based with bcrypt)
   - Routes requests to appropriate services
   - Supports REST and GraphQL (Strawberry)
   - WebSocket support at `/ws`

2. **Budget Service** (`services/budget-service/`) - Port 8001
   - Multi-account tracking (bank, savings, cash, credit)
   - Transaction management with categories and tags
   - Budget allocation and monitoring
   - Multi-currency support
   - Recurring transactions
   - Uses PostgreSQL + Redis

3. **Portfolio Service** (`services/portfolio-service/`) - Port 8002
   - Investment tracking (stocks, ETFs, crypto, bonds)
   - Real-time price fetching (Alpha Vantage, CoinGecko)
   - Performance metrics (ROI, XIRR, TWR, Sharpe ratio)
   - Asset allocation analysis
   - Background jobs via Celery worker (uses Redis as broker)
   - Uses PostgreSQL + Redis

4. **Notification Service** (`services/notification-service/`) - Port 8003
   - Email, Telegram, WebPush notifications
   - Event processing
   - Webhook dispatching
   - Uses Redis only

5. **Frontend** (`frontend/`) - Port 3000
   - React/Next.js PWA with Tailwind CSS
   - Server-side rendered
   - Real-time updates via WebSocket

### Infrastructure Components

- **PostgreSQL** (port 5432): Primary database with schema-per-service approach
- **Redis** (port 6379): Caching, session storage, Celery broker, pub/sub (uses different DB indexes per service)
- **MinIO** (port 9000/9001): S3-compatible object storage for documents and backups

## Development Commands

### Starting Services

```bash
# Start entire stack (recommended)
make dev
# or
docker-compose up -d

# View logs
make logs
# or
docker-compose logs -f

# Stop services
make down
# or
docker-compose down

# Clean up (including volumes)
make clean
```

### Working with Individual Services

Each Python service follows the same structure:

```bash
# Navigate to service directory
cd services/<service-name>

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # for dev tools

# Run service locally (without Docker)
uvicorn app.main:app --reload --port <port>

# Run tests
pytest

# Run linting
ruff check .
black --check .

# Format code
black .
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Run linting
npm run lint

# Build for production
npm run build
```

### Database Migrations

Services use Alembic for database migrations:

```bash
cd services/<service-name>

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Running Tests

```bash
# All services
make test

# Single service
cd services/budget-service
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_api.py

# Specific test
pytest tests/test_api.py::test_function_name
```

## Service Structure

Each Python service follows this structure:

```
services/<service-name>/
├── app/
│   ├── api/v1/              # API endpoints
│   │   └── endpoints/       # Individual route files
│   ├── core/                # Core functionality
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # DB connection
│   │   ├── security.py      # Password/JWT utils
│   │   └── auth.py          # Auth middleware
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── main.py              # FastAPI app entry point
├── tests/                   # Tests
├── alembic/                 # Database migrations
├── requirements.txt         # Dependencies
└── Dockerfile              # Container definition
```

## Authentication System

All services use JWT-based authentication through the API Gateway:

- **Token Types**: Access tokens (30 min) and refresh tokens (7 days)
- **Password Requirements**: Min 8 chars, uppercase, lowercase, digit
- **User Roles**: `user` (default), `premium`, `admin`
- **Protected Routes**: Use `get_current_user` dependency
- **Role-Based Access**: Use `RoleChecker` or convenience dependencies (`require_admin`, `require_premium`)

Key auth files in budget-service:
- `app/core/security.py`: Password hashing, JWT generation/validation
- `app/core/auth.py`: Auth middleware and RBAC
- `app/api/v1/endpoints/auth.py`: Auth endpoints
- See `services/budget-service/AUTH_README.md` for complete details

## API Documentation

When services are running, access Swagger UI:
- API Gateway: http://localhost:8000/docs
- Budget Service: http://localhost:8001/docs
- Portfolio Service: http://localhost:8002/docs
- Notification Service: http://localhost:8003/docs

## Common Patterns

### Environment Variables

Configuration is managed through environment variables. See `.env.example` for required variables. Copy it to create local config:

```bash
cp .env.example .env
# Edit .env with your values
```

### Database Connections

All services use SQLAlchemy with async support (asyncpg). Connection URLs follow pattern:
```
postgresql://fincloud:fincloud_dev_password@postgres:5432/fincloud
```

### Redis Usage

Each service uses a different Redis database index:
- Budget Service: DB 0
- Portfolio Service: DB 1
- Portfolio Celery: DB 2
- Notification Service: DB 3
- API Gateway: DB 4

### Celery Workers

Portfolio service uses Celery for background tasks (price updates, analytics calculations):

```bash
# Run worker (via Docker)
docker-compose up portfolio-worker

# Or manually
cd services/portfolio-service
celery -A app.celery_app worker --loglevel=info
```

## Code Quality

- **Python**: Follow PEP 8, use type hints, write docstrings
- **Formatting**: Use `black` for Python code formatting
- **Linting**: Use `ruff` for Python linting
- **Testing**: Write tests for new features, aim for good coverage
- **Commit Messages**: Follow conventional commits format (`feat:`, `fix:`, `docs:`, etc.)

## Kubernetes Deployment

```bash
# Deploy to K8s using Helm
make deploy-k8s

# Or manually
helm upgrade --install fincloud infrastructure/helm/fincloud \
  --namespace fincloud \
  --create-namespace

# Port forward to access
kubectl port-forward -n fincloud svc/fincloud-frontend 3000:3000
```

## Important Notes

- **Multi-currency**: Budget service supports multiple currencies with automatic exchange rates
- **API Versioning**: All endpoints are versioned under `/api/v1/`
- **GraphQL**: Available at API Gateway `/graphql` endpoint
- **WebSocket**: Real-time updates available at `/ws`
- **CORS**: Configured in API Gateway for frontend origins
- **Health Checks**: All services have health check endpoints for container orchestration
- **External APIs**: Portfolio service requires API keys for price data (Alpha Vantage, CoinGecko) - set in `.env`
- **Database Initialization**: `infrastructure/docker/init-db.sql` sets up initial database structure
- **Monitoring**: Services expose Prometheus metrics for monitoring

## Troubleshooting

- **Database connection issues**: Check if PostgreSQL container is healthy and migrations are applied
- **Redis connection issues**: Verify Redis is running and check service-specific DB index
- **Authentication issues**: Ensure JWT_SECRET matches between services, check token expiration
- **Celery tasks not running**: Verify portfolio-worker container is running and can connect to Redis DB 2
- **Port conflicts**: Ensure ports 3000, 8000-8003, 5432, 6379, 9000-9001 are available
