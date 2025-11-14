'use client'

import AppLayout from '@/components/layout/AppLayout'

export default function ReportsPage() {
  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Financial Reports
          </h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Analyze your financial data with detailed reports
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-8 text-center">
          <p className="text-gray-500 dark:text-gray-400">
            Reports and analytics features coming soon...
          </p>
        </div>
      </div>
    </AppLayout>
  )
}
