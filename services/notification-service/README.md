# Notification Service

Event-driven notification service for FinCloud.

## Features

- Email notifications (SMTP)
- Telegram notifications
- WebPush notifications
- Webhook dispatching
- Event queuing with Redis
- Template management

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn app.main:app --reload --port 8003
```

## Supported Notifications

- Budget threshold alerts
- Transaction created
- Portfolio performance updates
- Price alerts
- Custom webhooks for automation (n8n, Home Assistant)

## Environment Variables

See `.env.example` in the root directory.
