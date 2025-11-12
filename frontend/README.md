# FinCloud Frontend

Modern, responsive PWA built with Next.js, React, and Tailwind CSS.

## Features

- Server-side rendering with Next.js 14
- TypeScript for type safety
- Tailwind CSS for styling
- Framer Motion for animations
- React Query for data fetching
- Zustand for state management
- Progressive Web App (PWA) capable
- Dark/Light theme support

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Type checking
npm run type-check

# Linting
npm run lint
```

## Project Structure

```
src/
├── app/              # Next.js app directory
├── components/       # React components
├── lib/             # Utility functions
├── hooks/           # Custom React hooks
└── stores/          # Zustand stores
```

## Environment Variables

Create a `.env.local` file:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## Docker

```bash
# Development
docker build -f Dockerfile.dev -t fincloud-frontend:dev .
docker run -p 3000:3000 fincloud-frontend:dev

# Production
docker build -f Dockerfile -t fincloud-frontend:prod .
docker run -p 3000:3000 fincloud-frontend:prod
```
