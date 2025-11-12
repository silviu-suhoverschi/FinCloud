# FinCloud Documentation

Welcome to the FinCloud documentation! FinCloud is a self-hosted, open-source personal finance and investment management platform.

## Overview

FinCloud combines the best features of budgeting tools (like Firefly III) and portfolio tracking platforms (like Ghostfolio) into a unified, cloud-native application.

### Key Features

- **💰 Budget Management**: Track expenses, manage budgets, and analyze spending patterns
- **📈 Portfolio Tracking**: Monitor investments with real-time price updates and performance analytics
- **🔐 Privacy-First**: Self-hosted with complete control over your financial data
- **🔌 Integration-Ready**: REST/GraphQL API, webhooks, n8n, Home Assistant support
- **🧩 Extensible**: Plugin framework for custom functionality
- **🌐 Cloud-Native**: Kubernetes-ready with Docker Compose support
- **📱 Modern UI**: Responsive PWA built with React and Next.js

## Quick Links

- [Quick Start Guide](getting-started/quickstart.md)
- [Installation Instructions](getting-started/installation.md)
- [API Reference](api/rest.md)
- [Architecture Overview](architecture/overview.md)

## Architecture

FinCloud uses a microservices architecture:

```
Frontend (React/Next.js)
        ↓
API Gateway (FastAPI)
        ↓
┌───────┼───────────┐
│       │           │
Budget  Portfolio  Notification
Service Service    Service
```

## Getting Help

- 📖 [Documentation](/)
- 💬 [GitHub Discussions](https://github.com/your-username/FinCloud/discussions)
- 🐛 [Issue Tracker](https://github.com/your-username/FinCloud/issues)
- 💡 [Feature Requests](https://github.com/your-username/FinCloud/issues/new?template=feature_request.md)

## Contributing

We welcome contributions! See our [Contributing Guide](development/contributing.md) to get started.

## License

FinCloud is licensed under the [AGPL-3.0 License](https://github.com/your-username/FinCloud/blob/main/LICENSE).
