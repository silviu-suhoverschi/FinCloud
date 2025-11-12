# Installation Guide

Complete installation guide for different deployment scenarios.

## Docker Compose (Recommended)

Perfect for homelab setups and local development.

### System Requirements

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM (8GB recommended)
- 20GB disk space

### Installation Steps

See [Quick Start Guide](quickstart.md) for basic Docker Compose setup.

### Custom Configuration

Create `docker-compose.override.yml` for custom settings:

```yaml
version: '3.8'

services:
  frontend:
    environment:
      - NODE_ENV=production
    ports:
      - "8080:3000"
```

## Kubernetes

For production-grade deployments with high availability.

### Prerequisites

- Kubernetes 1.20+
- Helm 3+
- kubectl configured
- Ingress controller (nginx recommended)
- cert-manager (for TLS)

### Installation

```bash
# Add Helm repository
helm repo add fincloud https://your-org.github.io/FinCloud
helm repo update

# Create namespace
kubectl create namespace fincloud

# Install FinCloud
helm install fincloud fincloud/fincloud \
  --namespace fincloud \
  --values custom-values.yaml
```

### Custom Values

Create `custom-values.yaml`:

```yaml
postgresql:
  auth:
    password: "your-secure-password"

ingress:
  enabled: true
  hosts:
    - host: fincloud.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: fincloud-tls
      hosts:
        - fincloud.yourdomain.com

budgetService:
  replicaCount: 3
  resources:
    requests:
      memory: "512Mi"
      cpu: "500m"
```

## Manual Installation

For custom setups or bare metal deployments.

### 1. Install Dependencies

```bash
# Python services
sudo apt-get install python3.12 postgresql redis-server

# Node.js for frontend
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 2. Set Up Database

```bash
sudo -u postgres createdb fincloud
sudo -u postgres createuser fincloud
sudo -u postgres psql -c "ALTER USER fincloud WITH PASSWORD 'your_password';"
```

### 3. Install Services

```bash
# Budget Service
cd services/budget-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start service
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### 4. Install Frontend

```bash
cd frontend
npm install
npm run build
npm start
```

## Environment Variables

Key environment variables to configure:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `JWT_SECRET` | Secret for JWT tokens | Generate with `openssl rand -hex 32` |
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage API key | `demo` |

## Post-Installation

### 1. Verify Installation

```bash
# Check services
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health

# Check frontend
curl http://localhost:3000
```

### 2. Create Admin User

Access the frontend and register your first user. The first user automatically becomes an admin.

### 3. Configure Backups

See [Backup Guide](../deployment/backup.md) for backup configuration.

## Upgrading

### Docker Compose

```bash
docker-compose pull
docker-compose up -d
```

### Kubernetes

```bash
helm upgrade fincloud fincloud/fincloud \
  --namespace fincloud \
  --values custom-values.yaml
```

## Troubleshooting

See [Troubleshooting Guide](../help/troubleshooting.md) for common issues.
