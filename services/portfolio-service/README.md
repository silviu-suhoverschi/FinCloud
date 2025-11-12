# Portfolio Service

Investment and portfolio management service for FinCloud.

## Features

- Multi-portfolio tracking
- Support for stocks, ETFs, crypto, bonds, and funds
- Automatic price fetching from multiple data providers
- Performance analytics (ROI, XIRR, TWR, Sharpe ratio)
- Asset allocation analysis
- Rebalancing recommendations
- Benchmark comparisons

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn app.main:app --reload --port 8002

# Run Celery worker
celery -A app.celery_app worker --loglevel=info

# Run Celery beat (scheduler)
celery -A app.celery_app beat --loglevel=info
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc

## Price Data Providers

- **Yahoo Finance**: Free, no API key required
- **Alpha Vantage**: Free tier available (5 API calls per minute)
- **CoinGecko**: Cryptocurrency data

## Environment Variables

See `.env.example` in the root directory.
