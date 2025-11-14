'use client'

import AppLayout from '@/components/layout/AppLayout'

export default function NotificationsPage() {
  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Notifications
          </h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Manage your notification preferences and view alerts
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-8 text-center">
          <p className="text-gray-500 dark:text-gray-400">
            No notifications at this time
          </p>
        </div>
      </div>
    </AppLayout>
  )
}
