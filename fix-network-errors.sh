#!/bin/bash

# Script to fix network errors by clearing Next.js build cache and restarting frontend

echo "=== Fixing Network Errors in FinCloud Frontend ==="
echo ""
echo "This script will:"
echo "1. Stop the frontend service"
echo "2. Remove the container and any anonymous volumes"
echo "3. Remove the local .next build cache"
echo "4. Restart the frontend service with correct environment variables"
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed or not in PATH"
    exit 1
fi

# Stop the frontend service
echo "Stopping frontend service..."
docker-compose stop frontend

# Remove the container and its anonymous volumes
echo "Removing frontend container and anonymous volumes..."
docker-compose rm -f -v frontend

# Remove the local .next directory if it exists
if [ -d "./frontend/.next" ]; then
    echo "Removing local .next build cache..."
    rm -rf ./frontend/.next
fi

# Start the frontend service again
echo "Starting frontend service with fresh build..."
docker-compose up -d frontend

echo ""
echo "=== Done! ==="
echo ""
echo "The frontend service has been restarted and will rebuild with correct environment variables."
echo "Please wait a few moments for the service to start (initial build may take 30-60 seconds)."
echo ""
echo "The frontend should now connect to: http://localhost:8000 (API Gateway)"
echo "You can check logs with: docker-compose logs -f frontend"
echo ""
echo "If the issue persists, you may need to:"
echo "1. Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)"
echo "2. Clear browser cache"
echo "3. Check the browser console for the debug message showing the API URL being used"
