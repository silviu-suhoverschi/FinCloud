# Network Error Fix Documentation

## Problem

The frontend application is showing network errors when trying to connect to the API:

```
GET http://budget-service:8001/api/v1/accounts/ net::ERR_NAME_NOT_RESOLVED
```

## Root Cause

The issue was caused by TWO problems:

1. **Docker Volume Caching**: The `docker-compose.yml` had an anonymous volume mount for `/app/.next` which preserved the Next.js build cache across container restarts, keeping old environment variables baked in.

2. **Environment Variable Embedding**: Next.js embeds `NEXT_PUBLIC_*` environment variables into the client-side JavaScript bundle at build time. The cached `.next` directory had `NEXT_PUBLIC_API_URL=http://budget-service:8001` (internal Docker hostname) instead of `http://localhost:8000` (API Gateway).

Why `budget-service:8001` doesn't work:
- `budget-service:8001` is a Docker internal hostname that only works within the Docker network
- The browser (running on the host machine) cannot resolve Docker service names
- The frontend must connect through the API Gateway at `http://localhost:8000`

## Solution

The fix involves two changes:

1. **Code Changes** (already applied):
   - Removed the `/app/.next` volume mount from `docker-compose.yml`
   - Added debug logging to `frontend/src/lib/api.ts`

2. **Clean Rebuild** (you need to run this):

### Quick Fix (Recommended)

Run the provided fix script:

```bash
./fix-network-errors.sh
```

This script will:
1. Stop the frontend service
2. Remove the container and anonymous volumes
3. Remove the local `.next` build cache
4. Restart the frontend service with correct environment variables

### Manual Fix

If you prefer to fix it manually:

```bash
# Stop and remove the frontend container with volumes
docker-compose stop frontend
docker-compose rm -f -v frontend

# Remove the local .next cache
rm -rf frontend/.next

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

The following files have been updated to fix this issue:

1. **`docker-compose.yml`** (FIXED) - Removed the problematic `/app/.next` volume mount:
   ```yaml
   frontend:
     environment:
       NEXT_PUBLIC_API_URL: http://localhost:8000
       NEXT_PUBLIC_WS_URL: ws://localhost:8000/ws
     volumes:
       - ./frontend:/app
       - /app/node_modules
       # REMOVED: - /app/.next (was caching old environment variables)
   ```

2. **`frontend/src/lib/api.ts`** (ENHANCED) - Added debug logging to show API URL:
   ```typescript
   const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

   // Debug: Log the API base URL being used
   if (typeof window !== 'undefined') {
     console.log('[API Config] Base URL:', API_BASE_URL)
   }
   ```

3. **`frontend/.env.local`** (created, not committed) - Local override for development:
   - `NEXT_PUBLIC_API_URL=http://localhost:8000`
   - `NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws`

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
