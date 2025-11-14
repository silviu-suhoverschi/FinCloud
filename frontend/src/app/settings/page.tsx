'use client'

import AppLayout from '@/components/layout/AppLayout'

export default function SettingsPage() {
  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Settings
          </h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Manage your account and application preferences
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Profile Settings
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Update your profile information and preferences
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Notification Preferences
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Configure how you receive notifications
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Currency Settings
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Set your default currency and exchange rate preferences
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              API Keys
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Manage API keys for external integrations
            </p>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
