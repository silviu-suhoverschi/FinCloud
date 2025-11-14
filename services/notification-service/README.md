# Notification Service

Event-driven notification service for FinCloud that handles multi-channel notifications including email, Telegram, and webhooks.

## Features

- **Email Notifications (SMTP)** - Fully customizable HTML/plain text emails
- **Telegram Notifications** - Real-time messaging via Telegram Bot API
- **Webhook Dispatching** - HTTP webhooks with signature verification for integrations
- **Event Queue (Redis)** - Reliable message queue for async processing
- **Template Management** - Jinja2-based templating system with custom filters
- **User Preferences** - Per-user notification settings and channel preferences
- **Multi-channel Support** - Send to multiple channels simultaneously
- **Retry Logic** - Automatic retry with exponential backoff for webhooks

## Architecture

The service uses an event-driven architecture:
1. Events are enqueued to Redis via the API
2. Background worker processes events from the queue
3. Events are dispatched to enabled channels based on user preferences
4. Templates are rendered and notifications are sent

```
API Endpoints → Redis Queue → Event Processor → Notification Services
                                                 ├─ Email (SMTP)
                                                 ├─ Telegram (Bot API)
                                                 └─ Webhooks (HTTP)
```

## Development

### Local Setup

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run the service
uvicorn app.main:app --reload --port 8003

# Or with environment variables
REDIS_URL=redis://localhost:6379/3 \
SMTP_HOST=smtp.gmail.com \
SMTP_USER=your-email@gmail.com \
SMTP_PASSWORD=your-app-password \
uvicorn app.main:app --reload --port 8003
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Fix linting issues
ruff check --fix .
```

## API Endpoints

### Notifications

#### POST /api/v1/notifications/send
Send a notification (enqueues for processing)

```json
{
  "user_id": "user-123",
  "notification_type": "budget_alert",
  "channels": ["email", "telegram"],
  "subject": "Budget Alert",
  "message": "Your budget has been exceeded",
  "data": {
    "budget_name": "Groceries",
    "spent": 520.00,
    "limit": 500.00
  },
  "priority": 2
}
```

#### POST /api/v1/notifications/event
Enqueue a notification event directly

```json
{
  "event_type": "budget_threshold_exceeded",
  "user_id": "user-123",
  "data": {
    "budget_name": "Groceries",
    "spent": 520.00,
    "limit": 500.00,
    "percentage": 104.0
  }
}
```

#### GET /api/v1/notifications/queue/stats
Get queue statistics

### Preferences

#### GET /api/v1/preferences/{user_id}
Get notification preferences for a user

#### PUT /api/v1/preferences/{user_id}
Update notification preferences

```json
{
  "email_enabled": true,
  "telegram_enabled": true,
  "email_address": "user@example.com",
  "telegram_chat_id": "123456789",
  "budget_alerts_enabled": true,
  "quiet_hours_enabled": true,
  "quiet_hours_start": "22:00",
  "quiet_hours_end": "08:00"
}
```

#### DELETE /api/v1/preferences/{user_id}
Delete (reset) notification preferences

### Webhooks

#### POST /api/v1/webhooks/test
Test a webhook configuration

```json
{
  "url": "https://example.com/webhook",
  "method": "POST",
  "payload": {"test": "data"},
  "secret": "optional-secret-for-signing"
}
```

## Supported Notifications

### Budget Alerts
- Budget threshold exceeded
- Budget threshold warning (80%+)
- Budget created/updated

### Transaction Notifications
- Transaction created
- Large transaction detected
- Recurring transaction processed

### Portfolio Alerts
- Portfolio value changed significantly
- Price target hit
- Price alert triggered

### System Notifications
- System updates
- Maintenance scheduled
- User action required

## Email Templates

Templates are located in `app/templates/email/` and use Jinja2:

- `budget_alert.txt` / `budget_alert.html` - Budget notifications
- `transaction_created.txt` / `transaction_created.html` - Transaction notifications
- More templates can be added for each notification type

### Template Variables

Common variables available in templates:
- `user_name` - User's display name
- `subject` - Notification subject
- `message` - Notification message
- `app_url` - Application URL
- Type-specific data from the event

### Custom Filters

- `currency(value, currency="USD")` - Format as currency

## Configuration

### Environment Variables

```bash
# Service
SERVICE_PORT=8003
LOG_LEVEL=info
ENVIRONMENT=development

# Redis
REDIS_URL=redis://localhost:6379/3

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@fincloud.example.com
SMTP_FROM_NAME=FinCloud
SMTP_USE_TLS=true

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token

# Webhook Settings
WEBHOOK_TIMEOUT=30
WEBHOOK_MAX_RETRIES=3
WEBHOOK_RETRY_DELAY=5

# Event Queue
EVENT_QUEUE_NAME=notifications:events
EVENT_PROCESSING_INTERVAL=1
EVENT_BATCH_SIZE=10
```

## Integrations

### n8n Automation

Use webhooks to integrate with n8n:
1. Set up webhook node in n8n
2. Configure webhook URL in user preferences
3. Receive notification events as JSON

### Home Assistant

Receive notifications in Home Assistant:
1. Create webhook automation
2. Set webhook URL in preferences
3. Process events in Home Assistant

### Custom Integrations

The service provides webhook dispatching with:
- HMAC-SHA256 signature verification
- Automatic retry with exponential backoff
- Custom headers support
- Multiple HTTP methods

## Docker Deployment

```bash
# Build image
docker build -t fincloud-notification-service .

# Run container
docker run -d \
  -p 8003:8003 \
  -e REDIS_URL=redis://redis:6379/3 \
  -e SMTP_HOST=smtp.gmail.com \
  -e SMTP_USER=user@gmail.com \
  -e SMTP_PASSWORD=password \
  --name notification-service \
  fincloud-notification-service
```

## Health Checks

The service provides health check endpoints:

- `GET /health` - Service health status
- `GET /info` - Service information and feature availability

## Monitoring

The service emits structured logs using structlog:
- Event processing status
- Notification delivery status
- Error tracking
- Performance metrics

## Security

- HMAC signature verification for webhooks
- TLS/SSL support for SMTP
- Secure credential storage
- No sensitive data in logs

## Performance

- Async I/O for all network operations
- Redis-backed event queue
- Concurrent event processing
- Connection pooling for SMTP

## Troubleshooting

### Email not sending
- Verify SMTP credentials
- Check SMTP_HOST and SMTP_PORT
- For Gmail, use App Passwords (not account password)
- Check firewall settings for SMTP port

### Telegram not working
- Verify bot token is correct
- Check that bot is started by user
- Verify chat ID is correct
- Test with /start command in Telegram

### Webhooks failing
- Check webhook URL is accessible
- Verify SSL certificate is valid
- Check webhook endpoint returns 200 status
- Review webhook service logs for retry attempts

### Events not processing
- Check Redis connection
- Verify event queue is running
- Check event processor logs
- Review queue length in /health endpoint

## Contributing

1. Write tests for new features
2. Follow code style (black + ruff)
3. Update documentation
4. Ensure tests pass (`pytest`)

## License

Part of FinCloud project - See root LICENSE file.
