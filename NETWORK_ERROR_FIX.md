# Network Error Fix Documentation

## Problem

The frontend application is showing network errors when trying to connect to the API:

```
GET http://budget-service:8001/api/v1/accounts/ net::ERR_NAME_NOT_RESOLVED
```

## Root Cause

The Next.js application has a cached build (`.next` directory) that was created with incorrect environment variables. The `NEXT_PUBLIC_API_URL` was likely set to `http://budget-service:8001` during an initial build, which is incorrect because:

1. `budget-service:8001` is a Docker internal hostname that only works within the Docker network
2. The browser (running on the host machine) cannot resolve Docker service names
3. The frontend should connect through the API Gateway at `http://localhost:8000`

## Solution

### Quick Fix (Recommended)

Run the provided fix script:

```bash
./fix-network-errors.sh
```

This script will:
1. Stop the frontend service
2. Remove the cached container
3. Restart the frontend service with correct environment variables

### Manual Fix

If you prefer to fix it manually:

```bash
# Stop and remove the frontend container
docker-compose stop frontend
docker-compose rm -f frontend

# Start the frontend service again
docker-compose up -d frontend

# Monitor the logs to ensure it starts correctly
docker-compose logs -f frontend
```

### Alternative: Full Cleanup

If the quick fix doesn't work, try a full cleanup:

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: This will remove all data)
docker-compose down -v

# Start services again
docker-compose up -d

# Wait for services to be healthy, then run migrations if needed
make migrate
```

## Verification

After applying the fix:

1. Wait for the frontend service to fully start (check logs: `docker-compose logs -f frontend`)
2. Open your browser and navigate to `http://localhost:3000`
3. Check the browser console - you should no longer see `ERR_NAME_NOT_RESOLVED` errors
4. The API requests should now go to `http://localhost:8000/api/v1/*` (API Gateway)

## Configuration Files

The following files have been updated/created to fix this issue:

1. **`frontend/.env.local`** (created) - Sets correct environment variables for local development:
   - `NEXT_PUBLIC_API_URL=http://localhost:8000`
   - `NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws`

2. **`docker-compose.yml`** (already correct) - Has correct environment variables:
   ```yaml
   frontend:
     environment:
       NEXT_PUBLIC_API_URL: http://localhost:8000
       NEXT_PUBLIC_WS_URL: ws://localhost:8000/ws
   ```

## Why This Happens

Next.js embeds `NEXT_PUBLIC_*` environment variables into the client-side JavaScript bundle at build time. If the environment variables change after the build, the old values remain cached in the `.next` directory until the build is cleared and regenerated.

## Prevention

To prevent this issue in the future:

1. Always ensure environment variables are set correctly before first build
2. After changing `NEXT_PUBLIC_*` environment variables in `docker-compose.yml`, restart the frontend service
3. If you see unexpected API URLs in browser console, check and clear the `.next` build cache

## Troubleshooting

If the issue persists after applying the fix:

1. **Check frontend logs:**
   ```bash
   docker-compose logs frontend
   ```

2. **Verify environment variables in container:**
   ```bash
   docker-compose exec frontend printenv | grep NEXT_PUBLIC
   ```
   Should show:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
   ```

3. **Check browser console:**
   - Open browser DevTools (F12)
   - Look at Network tab to see which URL is being called
   - Should see requests to `localhost:8000`, not `budget-service:8001`

4. **Hard refresh browser:**
   - Press Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
   - This clears browser cache and reloads all assets

5. **Check if API Gateway is running:**
   ```bash
   docker-compose ps
   curl http://localhost:8000/health || echo "API Gateway not responding"
   ```

## Related Files

- `frontend/src/lib/api.ts` - Axios configuration with API base URL
- `frontend/src/lib/budget.ts` - Budget service API calls
- `frontend/next.config.js` - Next.js configuration with environment variables
- `docker-compose.yml` - Docker services configuration
- `.env.example` - Example environment variables (shows correct values)
