'use client'

import AppLayout from '@/components/layout/AppLayout'

export default function PortfolioPage() {
  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Portfolio Tracking
          </h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Monitor your investments and track performance
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-8 text-center">
          <p className="text-gray-500 dark:text-gray-400">
            Portfolio tracking features coming soon...
          </p>
        </div>
      </div>
    </AppLayout>
  )
}
