# Quick Start Guide

Get FinCloud up and running in minutes with Docker Compose.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/FinCloud.git
cd FinCloud
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and update the following values:

```bash
# Generate a secure JWT secret
JWT_SECRET=$(openssl rand -hex 32)

# Set your API keys (optional for initial setup)
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

### 3. Start Services

```bash
# Using Docker Compose
docker-compose up -d

# Or using Make
make dev
```

### 4. Access FinCloud

After services start (takes 1-2 minutes):

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001

Default credentials will be shown in the logs on first startup.

## Next Steps

1. **Create an Account**: Register at http://localhost:3000/register
2. **Add a Budget**: Set up your first budget category
3. **Add Transactions**: Start tracking your expenses
4. **Create Portfolio**: Add your investment accounts
5. **Explore API**: Visit http://localhost:8000/docs

## Troubleshooting

### Services not starting?

```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart
```

### Database issues?

```bash
# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

### Port conflicts?

Edit `docker-compose.yml` and change port mappings:

```yaml
ports:
  - "3001:3000"  # Change left side only
```

## What's Next?

- [Full Installation Guide](installation.md)
- [Configuration Options](configuration.md)
- [API Documentation](../api/rest.md)
