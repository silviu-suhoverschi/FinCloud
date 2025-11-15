import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Define public routes that don't require authentication
const publicRoutes = ['/auth/login', '/auth/register', '/auth/forgot-password']

// Define routes that should redirect to dashboard if already authenticated
const authRoutes = ['/auth/login', '/auth/register']

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Get token from cookies or check if we should verify localStorage
  // Note: We need to handle this on client side since tokens are in localStorage
  // For now, we'll use a cookie-based approach for SSR
  const token = request.cookies.get('access_token')?.value

  // Check if the current route is public
  const isPublicRoute = publicRoutes.some(route => pathname.startsWith(route))

  // Check if the current route is an auth route
  const isAuthRoute = authRoutes.some(route => pathname.startsWith(route))

  // Allow access to root path
  if (pathname === '/') {
    // If authenticated, redirect to dashboard
    if (token) {
      return NextResponse.redirect(new URL('/dashboard', request.url))
    }
    // If not authenticated, redirect to login
    return NextResponse.redirect(new URL('/auth/login', request.url))
  }

  // If user is on an auth route and already has a token, redirect to dashboard
  if (isAuthRoute && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  // If the route is not public and user is not authenticated, redirect to login
  if (!isPublicRoute && !token) {
    const loginUrl = new URL('/auth/login', request.url)
    loginUrl.searchParams.set('redirect', pathname)
    return NextResponse.redirect(loginUrl)
  }

  return NextResponse.next()
}

// Configure which routes should be processed by this middleware
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (public directory)
     */
    '/((?!api|_next/static|_next/image|favicon.ico|.*\\..*|public).*)',
  ],
}
