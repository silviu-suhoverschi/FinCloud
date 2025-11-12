# Architecture Overview

FinCloud uses a cloud-native microservices architecture designed for scalability, maintainability, and extensibility.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Clients                               │
│              (Web, Mobile PWA, API)                      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ HTTPS/WSS
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  API Gateway                             │
│         (FastAPI, GraphQL, WebSocket)                    │
│       Auth, Rate Limiting, Request Routing              │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────────┐
        │              │                  │
┌───────▼────────┐ ┌──▼────────────┐ ┌──▼──────────────┐
│ Budget Service │ │Portfolio Svc  │ │Notification Svc │
│   (FastAPI)    │ │(FastAPI+Celery)│ │   (FastAPI)    │
└───────┬────────┘ └──────┬────────┘ └─────┬───────────┘
        │                  │                 │
        │    ┌─────────────┼─────────────┐  │
        │    │             │             │  │
┌───────▼────▼──────┐ ┌───▼──────┐ ┌───▼──▼──────┐
│   PostgreSQL      │ │  Redis   │ │   MinIO     │
│   (Database)      │ │ (Cache)  │ │  (Storage)  │
└───────────────────┘ └──────────┘ └─────────────┘
```

## Core Components

### Frontend Layer

**Technology**: React, Next.js, TailwindCSS

- Server-side rendered PWA
- Responsive design for mobile and desktop
- Real-time updates via WebSocket
- Offline capability
- Dark/Light theme support

### API Gateway

**Technology**: FastAPI, Strawberry GraphQL

**Responsibilities**:
- Request routing to microservices
- Authentication and authorization
- Rate limiting
- API documentation aggregation
- WebSocket connections
- CORS handling

**Endpoints**:
- REST API: `/api/v1/*`
- GraphQL: `/graphql`
- WebSocket: `/ws`

### Budget Service

**Technology**: FastAPI, SQLAlchemy, PostgreSQL

**Responsibilities**:
- Account management
- Transaction tracking
- Budget allocation and monitoring
- Category management
- Recurring transactions
- Multi-currency support
- Financial reports

**Key Features**:
- ACID transactions
- Full-text search
- Automatic categorization
- CSV/OFX import

### Portfolio Service

**Technology**: FastAPI, Celery, PostgreSQL

**Responsibilities**:
- Portfolio management
- Holdings tracking
- Price fetching from multiple sources
- Performance analytics (ROI, XIRR, TWR)
- Asset allocation analysis
- Rebalancing recommendations

**Background Jobs**:
- Price updates (hourly)
- Performance calculations
- Dividend tracking
- News aggregation

### Notification Service

**Technology**: FastAPI, Redis

**Responsibilities**:
- Email notifications
- Telegram messages
- WebPush notifications
- Webhook dispatching
- Event processing

**Event Types**:
- Budget threshold exceeded
- Transaction created
- Portfolio performance alerts
- Price alerts

## Data Layer

### PostgreSQL

- Primary data store
- Schema-per-service approach
- Migrations via Alembic
- Connection pooling

### Redis

- Session storage
- Caching layer
- Celery message broker
- Real-time pub/sub

### MinIO

- Object storage (S3-compatible)
- Document uploads
- Export files
- Backup storage

## Communication Patterns

### Synchronous (REST)

Used for:
- Real-time user requests
- CRUD operations
- Data queries

### Asynchronous (Events)

Used for:
- Background processing
- Price updates
- Notifications
- Analytics calculations

### Real-time (WebSocket)

Used for:
- Live updates
- Notifications
- Price streaming
- Collaboration features

## Security Architecture

### Authentication Flow

```
1. User → Frontend: Login credentials
2. Frontend → API Gateway: POST /auth/login
3. API Gateway → Auth Service: Validate credentials
4. Auth Service: Generate JWT token
5. API Gateway → Frontend: Return JWT + refresh token
6. Frontend: Store tokens (httpOnly cookies)
7. Frontend → API Gateway: Subsequent requests with JWT
8. API Gateway: Validate JWT, forward to services
```

### Authorization

- Role-based access control (RBAC)
- Resource-level permissions
- Service-to-service authentication
- API key support for external integrations

## Scalability

### Horizontal Scaling

All services are stateless and can be horizontally scaled:

```yaml
replicas:
  api-gateway: 3
  budget-service: 2
  portfolio-service: 2
  notification-service: 1
  frontend: 2
```

### Database Scaling

- Read replicas for heavy read operations
- Connection pooling
- Query optimization
- Indexes on frequently queried columns

### Caching Strategy

- API responses (TTL: 5 minutes)
- User sessions (TTL: 24 hours)
- Price data (TTL: 1 hour)
- Static assets (CDN)

## Monitoring & Observability

### Metrics

- Prometheus metrics from all services
- Custom business metrics
- Request rates and latencies
- Error rates

### Logging

- Structured JSON logs
- Centralized with Loki
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Tracing

- Distributed tracing with OpenTelemetry
- Request flow across services
- Performance bottleneck identification

## Deployment Architecture

### Development

- Docker Compose
- Local PostgreSQL, Redis, MinIO
- Hot reload for all services

### Staging/Production

- Kubernetes cluster
- Managed PostgreSQL (RDS/Cloud SQL)
- Managed Redis (ElastiCache)
- S3 or equivalent object storage
- CDN for static assets
- Load balancer
- Auto-scaling

## Design Principles

1. **Microservices**: Loosely coupled, independently deployable
2. **API-First**: Well-documented REST and GraphQL APIs
3. **Cloud-Native**: Kubernetes-ready, containerized
4. **Security**: Zero-trust, encrypted communication
5. **Observability**: Comprehensive monitoring and logging
6. **Extensibility**: Plugin system for custom functionality

## Future Enhancements

- GraphQL subscriptions for real-time updates
- Event sourcing for audit trail
- CQRS for read/write optimization
- Service mesh (Istio) for advanced traffic management
- Multi-tenancy support
