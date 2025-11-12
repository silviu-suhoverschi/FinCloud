# API Gateway

Central API Gateway for FinCloud - handles routing, authentication, and GraphQL.

## Features

- Request routing to microservices
- Authentication & authorization (OAuth2/JWT)
- Rate limiting
- GraphQL API endpoint
- WebSocket support
- API documentation aggregation

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn app.main:app --reload --port 8000
```

## Endpoints

- REST API: `http://localhost:8000/api/v1/*`
- GraphQL: `http://localhost:8000/graphql`
- Docs: `http://localhost:8000/docs`

## Environment Variables

See `.env.example` in the root directory.
