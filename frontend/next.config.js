/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  swcMinify: true,

  // PWA configuration
  // Note: optimizeCss removed as it requires critters package
  // and may cause build issues in Docker environments

  // Environment variables exposed to the browser
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws',
  },

  // Image optimization
  images: {
    domains: ['localhost'],
  },
}

module.exports = nextConfig
