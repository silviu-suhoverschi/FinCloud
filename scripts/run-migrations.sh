#!/bin/bash

# Script to run database migrations for FinCloud services
# This applies all pending Alembic migrations to the database

set -e

echo "================================================"
echo "FinCloud Database Migration Runner"
echo "================================================"
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: docker-compose is not installed or not in PATH"
    exit 1
fi

# Check if services are running
if ! docker-compose ps | grep -q "fincloud-budget-service"; then
    echo "ERROR: Services are not running. Please start them first with 'make dev' or 'docker-compose up -d'"
    exit 1
fi

echo "Running Budget Service migrations..."
echo "-----------------------------------"
docker-compose exec budget-service alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✓ Budget Service migrations completed successfully"
else
    echo "✗ Budget Service migrations failed"
    exit 1
fi

echo ""
echo "Running Portfolio Service migrations..."
echo "---------------------------------------"
docker-compose exec portfolio-service alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✓ Portfolio Service migrations completed successfully"
else
    echo "✗ Portfolio Service migrations failed"
    exit 1
fi

echo ""
echo "================================================"
echo "All migrations completed successfully!"
echo "================================================"
echo ""
echo "You can now use the application. The 'theme' column"
echo "has been added to the users table."
