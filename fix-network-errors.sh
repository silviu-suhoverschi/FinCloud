#!/bin/bash

# Script to fix network errors by clearing Next.js build cache and restarting frontend

echo "=== Fixing Network Errors in FinCloud Frontend ==="
echo ""
echo "This script will:"
echo "1. Stop the frontend service"
echo "2. Remove the cached .next build directory"
echo "3. Restart the frontend service with correct environment variables"
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed or not in PATH"
    exit 1
fi

# Stop the frontend service
echo "Stopping frontend service..."
docker-compose stop frontend

# Remove the Next.js build cache volume
echo "Removing Next.js build cache..."
docker-compose rm -f frontend

# Optionally remove the volume (uncomment if needed)
# docker volume ls -q | grep fincloud | grep next | xargs -r docker volume rm

# Start the frontend service again
echo "Starting frontend service with fresh build..."
docker-compose up -d frontend

echo ""
echo "=== Done! ==="
echo ""
echo "The frontend service has been restarted and will rebuild with correct environment variables."
echo "Please wait a few moments for the service to start, then refresh your browser."
echo ""
echo "The frontend should now connect to: http://localhost:8000 (API Gateway)"
echo "You can check logs with: docker-compose logs -f frontend"
