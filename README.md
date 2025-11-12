# FinCloud 🏦

> Self-hosted, privacy-first personal finance and investment management platform

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=flat&logo=kubernetes&logoColor=white)](https://kubernetes.io/)

## Overview

FinCloud combines the best of **Firefly III** (budgeting & expense tracking) and **Ghostfolio** (portfolio & wealth analytics) into a unified, cloud-native platform. Designed for self-hosting, it gives you complete control over your financial data while providing modern automation and integration capabilities.

### Key Features

- 💰 **Budget Management**: Multi-account tracking, automated transaction import, smart categorization
- 📈 **Portfolio Tracking**: Stocks, ETFs, crypto, bonds with real-time performance metrics
- 🔐 **Privacy-First**: Self-hosted with OIDC authentication and full audit logs
- 🔌 **Integration-Ready**: REST/GraphQL API, webhooks, n8n, Home Assistant
- 🧩 **Plugin Framework**: Extensible architecture for custom functionality
- 🌐 **Cloud-Native**: Kubernetes-ready with Helm charts and Docker Compose support
- 📱 **Modern PWA**: Responsive React/Next.js interface with offline capability

## Quick Start

### Prerequisites

- Docker & Docker Compose
- (Optional) Kubernetes cluster with Helm 3+

### Local Development

```bash
# Clone the repository
git clone https://github.com/your-username/FinCloud.git
cd FinCloud

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# API Gateway: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Kubernetes Deployment

```bash
# Add Helm repository
helm repo add fincloud https://your-org.github.io/FinCloud

# Install FinCloud
helm install fincloud fincloud/fincloud \
  --namespace fincloud \
  --create-namespace

# Port forward to access
kubectl port-forward -n fincloud svc/fincloud-frontend 3000:3000
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (PWA)                       │
│                    React + Next.js + Tailwind                │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                      API Gateway                             │
│                  FastAPI + GraphQL + Auth                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼────────┐ ┌──────▼────────┐ ┌──────▼──────────┐
│ Budget Service │ │Portfolio Svc  │ │Notification Svc │
│   FastAPI      │ │ Celery+Python │ │   FastAPI       │
│   PostgreSQL   │ │   PostgreSQL  │ │     Redis       │
└────────────────┘ └───────────────┘ └─────────────────┘
```

## Repository Structure

```
FinCloud/
├── services/
│   ├── api-gateway/          # FastAPI API Gateway & GraphQL
│   ├── budget-service/       # Budget & transaction management
│   ├── portfolio-service/    # Investment tracking & analytics
│   ├── notification-service/ # Events & webhooks
│   └── auth-service/         # Authentication configuration
├── frontend/                 # React/Next.js PWA
├── infrastructure/
│   ├── docker/              # Docker Compose configs
│   ├── helm/                # Helm charts
│   └── kubernetes/          # Raw K8s manifests
├── docs/                    # MkDocs documentation
├── scripts/                 # Utility scripts
└── .github/workflows/       # CI/CD pipelines
```

## Documentation

Full documentation is available at [docs/](./docs/):

- [Architecture Overview](./docs/architecture.md)
- [API Reference](./docs/api-reference.md)
- [Deployment Guide](./docs/deployment.md)
- [Plugin Development](./docs/plugin-development.md)
- [Contributing Guide](./CONTRIBUTING.md)

## Core Modules

### Budget Management
- Multi-account support (bank, savings, cash, credit)
- Automated transaction import (CSV/OFX/QIF)
- Smart categorization with rules
- Multi-currency with auto exchange rates
- Recurring transactions and budgets
- Visual reports and analytics

### Portfolio Management
- Multi-portfolio tracking (stocks, ETFs, crypto, bonds)
- Automatic price fetching (Yahoo Finance, Alpha Vantage, CoinGecko)
- Performance metrics (ROI, XIRR, TWR, Sharpe ratio)
- Asset allocation analysis
- Rebalancing recommendations
- Benchmark comparisons

### Integrations
- REST & GraphQL API
- Webhooks for events
- n8n workflow integration
- Home Assistant sensors
- Email/Telegram/WebPush notifications

## Development Roadmap

- [x] **Phase 0**: Project setup & architecture (Current)
- [ ] **Phase 1 - MVP** (3 months): Core budget + portfolio + UI
- [ ] **Phase 2 - Integrations** (2 months): n8n, HA, webhooks, GraphQL
- [ ] **Phase 3 - AI & Plugins** (4 months): Plugin SDK, ML models
- [ ] **Phase 4 - Mobile** (2 months): PWA optimization

## Tech Stack

| Layer          | Technology                                      |
|----------------|-------------------------------------------------|
| Frontend       | React, Next.js, TailwindCSS, Framer Motion     |
| API Gateway    | FastAPI, GraphQL (Strawberry), OAuth2          |
| Services       | Python, FastAPI, Celery, SQLAlchemy            |
| Databases      | PostgreSQL, Redis                               |
| Storage        | MinIO (S3-compatible)                          |
| Auth           | Keycloak / OAuth2 Proxy                        |
| Orchestration  | Kubernetes, Helm, Docker Compose               |
| CI/CD          | GitHub Actions, ArgoCD                         |
| Monitoring     | Prometheus, Grafana, Loki                      |

## Contributing

We welcome contributions! Please see our [Contributing Guide](./CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install dependencies for each service
cd services/budget-service
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linting
ruff check .
```

## Security

- HTTPS enforced (cert-manager / Let's Encrypt)
- OIDC authentication with 2FA support
- Role-based access control (RBAC)
- Full audit logging
- Automated backups
- GDPR compliance

For security concerns, please email: security@fincloud.dev

## License

This project is licensed under the **AGPL-3.0 License** - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Inspired by:
- [Firefly III](https://www.firefly-iii.org/) - Budget management
- [Ghostfolio](https://ghostfol.io/) - Portfolio tracking
- The open-source community

## Support

- 📖 [Documentation](./docs/)
- 💬 [Discussions](https://github.com/your-username/FinCloud/discussions)
- 🐛 [Issue Tracker](https://github.com/your-username/FinCloud/issues)
- 📧 Email: support@fincloud.dev

---

**Built with ❤️ for financial independence and privacy**
