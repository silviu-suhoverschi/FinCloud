# Budget Service

Budget and transaction management service for FinCloud.

## Features

- Multi-account support (bank, savings, cash, credit)
- Transaction management with categories and tags
- Budget tracking and allocation
- Multi-currency support
- Recurring transactions
- Smart categorization rules

## Development

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run locally
uvicorn app.main:app --reload --port 8001

# Run tests
pytest

# Run linting
ruff check .
black --check .
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Environment Variables

See `.env.example` in the root directory.
