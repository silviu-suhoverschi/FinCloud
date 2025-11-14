# API Gateway

The API Gateway is the central entry point for all client requests to the FinCloud platform. It handles authentication, rate limiting, request routing, and service health monitoring.

## Features

### 1. Request Routing
- **Service Proxy**: Routes requests to appropriate microservices
- **Path-based routing**: Automatically routes based on URL path
  - `/api/v1/budget/*` → Budget Service
  - `/api/v1/portfolio/*` → Portfolio Service
  - `/api/v1/notifications/*` → Notification Service
  - `/api/v1/auth/*` → Budget Service (auth endpoints)
  - `/api/v1/users/*` → Budget Service (user management)

### 2. Authentication Middleware
- **JWT Token Validation**: Validates JWT tokens cryptographically (no database lookup)
- **User Context Injection**: Injects user information into request state
- **Public Path Management**: Configurable list of public endpoints
- **Token Information**: Extracts user_id, email, and role from tokens

Public endpoints (no authentication required):
- `/`, `/health`, `/docs`, `/redoc`
- `/api/v1/auth/register`
- `/api/v1/auth/login`
- `/api/v1/auth/refresh`
- `/api/v1/auth/password-reset/*`

### 3. Rate Limiting
- **Redis-based**: Uses Redis for distributed rate limiting
- **Sliding Window**: Implements sliding window algorithm
- **Multi-tier Limits**:
  - Per minute: 60 requests/min (configurable)
  - Per hour: 1000 requests/hour (configurable)
- **User-based**: Limits per authenticated user
- **IP-based**: Falls back to IP address for unauthenticated requests
- **Response Headers**: Includes rate limit info in response headers

Rate limit headers:
- `X-RateLimit-Limit-Minute`: Requests allowed per minute
- `X-RateLimit-Remaining-Minute`: Remaining requests this minute
- `X-RateLimit-Limit-Hour`: Requests allowed per hour
- `X-RateLimit-Remaining-Hour`: Remaining requests this hour
- `Retry-After`: Seconds until rate limit resets (on 429 response)

### 4. Circuit Breaker Pattern
- **Failure Detection**: Tracks failures to backend services
- **Automatic Failover**: Opens circuit after threshold failures
- **Recovery Testing**: Half-open state tests service recovery
- **Per-Service**: Independent circuit breakers for each service

Circuit breaker states:
- **CLOSED**: Normal operation, requests pass through
- **OPEN**: Service failing, requests fail fast with 503
- **HALF_OPEN**: Testing recovery, limited requests allowed

Configuration:
- Failure threshold: 5 failures (configurable)
- Recovery timeout: 60 seconds (configurable)
- Success threshold for recovery: 3 successful requests

### 5. Request/Response Logging
- **Structured Logging**: JSON-formatted logs with structlog
- **Request ID**: Unique ID for each request (UUID)
- **Timing Information**: Process time for each request
- **User Context**: Logs user_id for authenticated requests
- **Error Tracking**: Detailed error logging with stack traces

Log fields:
- `request_id`: Unique request identifier
- `method`: HTTP method
- `path`: Request path
- `status_code`: Response status code
- `process_time`: Request processing time
- `user_id`: Authenticated user ID (if any)
- `client_ip`: Client IP address
- `user_agent`: User agent string

Response headers:
- `X-Request-ID`: Request identifier
- `X-Process-Time`: Processing time in seconds

### 6. Health Check Aggregation
- **Gateway Health**: Simple health check for the gateway itself
- **Service Health**: Checks health of all backend services
- **Redis Health**: Monitors Redis connection status
- **Circuit Breaker Status**: Reports circuit breaker states
- **Kubernetes Probes**: Separate liveness and readiness endpoints

Endpoints:
- `GET /health` - Simple gateway health check
- `GET /api/v1/health` - Alias for /health
- `GET /api/v1/health/detailed` - Comprehensive health with all services
- `GET /api/v1/health/live` - Kubernetes liveness probe
- `GET /api/v1/health/ready` - Kubernetes readiness probe
- `GET /api/v1/status` - API status and configuration info

### 7. CORS Configuration
- **Configurable Origins**: Environment-based origin configuration
- **Credentials Support**: Allows cookies and authorization headers
- **Header Exposure**: Exposes custom headers to clients
- **Method Support**: Allows all HTTP methods

Default CORS configuration:
- Allowed origins: `http://localhost:3000`, `http://localhost:8000`
- Allow credentials: `true`
- Allowed methods: All
- Allowed headers: All
- Exposed headers: `X-Request-ID`, `X-Process-Time`, `X-RateLimit-*`

### 8. Unified OpenAPI Documentation
- **Auto-generated**: FastAPI automatically generates OpenAPI spec
- **Comprehensive**: Includes all gateway endpoints and documentation
- **Interactive**: Swagger UI and ReDoc available
- **Service Information**: Documents all backend services

Documentation URLs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        API Gateway                          │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ CORS Middleware                                       │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↓                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Logging Middleware (Request ID, Timing)               │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↓                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Authentication Middleware (JWT Validation)            │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↓                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Rate Limiting Middleware (Redis)                      │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↓                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Service Proxy (Circuit Breaker)                       │ │
│  │                                                         │ │
│  │  • Budget Service (8001)                              │ │
│  │  • Portfolio Service (8002)                           │ │
│  │  • Notification Service (8003)                        │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

Environment variables (see `.env.example`):

```bash
# Service Configuration
SERVICE_NAME=api-gateway
SERVICE_PORT=8000
ENVIRONMENT=development
LOG_LEVEL=info

# Security
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256

# Redis (DB 4 for API Gateway)
REDIS_URL=redis://localhost:6379/4

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Backend Services
BUDGET_SERVICE_URL=http://budget-service:8001
PORTFOLIO_SERVICE_URL=http://portfolio-service:8002
NOTIFICATION_SERVICE_URL=http://notification-service:8003

# Circuit Breaker
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_RECOVERY_TIMEOUT=60

# Request Timeout
REQUEST_TIMEOUT=30
```

## Directory Structure

```
services/api-gateway/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── health.py          # Health check endpoints
│   │       └── routes.py          # Service routing endpoints
│   ├── core/
│   │   ├── config.py              # Configuration management
│   │   ├── security.py            # JWT validation utilities
│   │   └── proxy.py               # Service proxy implementation
│   ├── middleware/
│   │   ├── auth.py                # Authentication middleware
│   │   ├── rate_limit.py          # Rate limiting middleware
│   │   ├── logging.py             # Request/response logging
│   │   └── circuit_breaker.py     # Circuit breaker pattern
│   └── main.py                    # FastAPI application
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Container definition
└── API_GATEWAY_README.md          # This file
```

## Running the Gateway

### Docker (Recommended)

```bash
# Start all services including gateway
docker-compose up -d api-gateway

# View logs
docker-compose logs -f api-gateway
```

### Local Development

```bash
cd services/api-gateway

# Install dependencies
pip install -r requirements.txt

# Run the gateway
uvicorn app.main:app --reload --port 8000

# Or use Python directly
python app/main.py
```

## API Usage Examples

### Authentication

```bash
# Register a new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "full_name": "John Doe"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'

# Response includes access_token and refresh_token
```

### Using Protected Endpoints

```bash
# Get user accounts (requires authentication)
curl http://localhost:8000/api/v1/budget/accounts \
  -H "Authorization: Bearer <your-access-token>"

# Create a transaction
curl -X POST http://localhost:8000/api/v1/budget/transactions \
  -H "Authorization: Bearer <your-access-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "amount": -50.00,
    "description": "Groceries",
    "category_id": 2
  }'
```

### Health Checks

```bash
# Simple health check
curl http://localhost:8000/health

# Detailed health with all services
curl http://localhost:8000/api/v1/health/detailed

# Check API status
curl http://localhost:8000/api/v1/status
```

## Monitoring

### Logs

The gateway produces structured JSON logs:

```json
{
  "event": "Incoming request",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "method": "GET",
  "path": "/api/v1/budget/accounts",
  "user_id": 1,
  "client_ip": "192.168.1.100",
  "timestamp": "2025-11-14T10:30:45.123456Z"
}
```

### Metrics

The gateway includes the following metrics in logs:
- Request count by endpoint
- Response time percentiles
- Error rates by service
- Rate limit violations
- Circuit breaker state changes

### Circuit Breaker Monitoring

Check circuit breaker status:

```bash
curl http://localhost:8000/api/v1/health/detailed | jq '.circuit_breakers'
```

Response:
```json
{
  "budget": {
    "state": "closed",
    "failure_count": 0,
    "time_until_retry": 0
  },
  "portfolio": {
    "state": "open",
    "failure_count": 5,
    "time_until_retry": 45
  }
}
```

## Error Handling

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing or invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error
- `503` - Service Unavailable (circuit breaker open or service down)
- `504` - Gateway Timeout (backend service timeout)

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

Rate limit errors include retry information:
```json
{
  "detail": "Rate limit exceeded: 60 requests per minute"
}
```

With headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Unix timestamp when limit resets
- `Retry-After`: Seconds to wait before retrying

## Security Considerations

1. **JWT Secret**: Change `JWT_SECRET` in production to a strong random value
2. **CORS Origins**: Restrict `CORS_ORIGINS` to your actual frontend domain in production
3. **Rate Limiting**: Adjust rate limits based on your usage patterns
4. **HTTPS**: Always use HTTPS in production (configure via reverse proxy)
5. **Redis Security**: Secure Redis with password and network isolation
6. **Timeout Configuration**: Adjust `REQUEST_TIMEOUT` based on expected response times

## Troubleshooting

### Gateway Won't Start

1. Check Redis connection:
   ```bash
   redis-cli -u redis://localhost:6379/4 ping
   ```

2. Verify environment variables are set correctly

3. Check logs for specific errors:
   ```bash
   docker-compose logs api-gateway
   ```

### Authentication Failures

1. Verify `JWT_SECRET` matches between gateway and budget service
2. Check token expiration time
3. Ensure Authorization header format: `Bearer <token>`

### Rate Limiting Issues

1. Check Redis connection and memory
2. Verify `REDIS_URL` points to correct database index (4)
3. Adjust rate limits if legitimate users are being blocked

### Circuit Breaker Triggered

1. Check backend service health:
   ```bash
   curl http://localhost:8001/health  # Budget service
   curl http://localhost:8002/health  # Portfolio service
   ```

2. View circuit breaker states:
   ```bash
   curl http://localhost:8000/api/v1/health/detailed
   ```

3. Wait for recovery timeout (default 60s) or restart affected service

### Service Connection Errors

1. Verify backend services are running:
   ```bash
   docker-compose ps
   ```

2. Check service URLs in configuration
3. Verify network connectivity between containers
4. Check Docker network configuration:
   ```bash
   docker network inspect fincloud_default
   ```

## Performance Tuning

### Redis Connection Pool

Adjust Redis connection pool size in code if needed:
```python
# In app/middleware/rate_limit.py
self.redis_client = redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    max_connections=50  # Adjust based on load
)
```

### HTTP Client Configuration

Tune httpx client settings in `app/core/proxy.py`:
```python
self.client = httpx.AsyncClient(
    timeout=httpx.Timeout(30.0),
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
)
```

### Circuit Breaker Settings

Adjust thresholds based on your SLA:
```bash
CIRCUIT_BREAKER_FAILURE_THRESHOLD=10  # More tolerant
CIRCUIT_BREAKER_RECOVERY_TIMEOUT=120  # Longer recovery time
```

## Development

### Adding New Routes

To add a new backend service:

1. Add service URL to `app/core/config.py`:
   ```python
   NEW_SERVICE_URL: str = "http://new-service:8004"
   ```

2. Add route in `app/api/v1/routes.py`:
   ```python
   @router.api_route("/newservice/{path:path}", methods=["GET", "POST", ...])
   async def proxy_to_new_service(request: Request, path: str):
       return await service_proxy.proxy_request(
           request=request,
           service_name="newservice",
           path=f"/api/v1/{path}"
       )
   ```

3. Update service URLs in proxy:
   ```python
   # In app/core/proxy.py
   self.service_urls = {
       ...
       "newservice": settings.NEW_SERVICE_URL,
   }
   ```

### Testing

```bash
# Install dev dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/

# With coverage
pytest --cov=app --cov-report=html tests/
```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Rate Limiting Algorithms](https://en.wikipedia.org/wiki/Rate_limiting)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
