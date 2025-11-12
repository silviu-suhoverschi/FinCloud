'use client'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="text-center">
        <h1 className="text-6xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
          FinCloud
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
          Self-hosted Personal Finance & Investment Management
        </p>
        <div className="flex gap-4 justify-center">
          <a
            href="/dashboard"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Go to Dashboard
          </a>
          <a
            href="/docs"
            className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition dark:bg-gray-700 dark:text-gray-200"
          >
            Documentation
          </a>
        </div>
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl">
          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
            <h3 className="text-lg font-semibold mb-2">💰 Budget Management</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Track expenses, manage budgets, and analyze spending patterns
            </p>
          </div>
          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
            <h3 className="text-lg font-semibold mb-2">📈 Portfolio Tracking</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Monitor investments, track performance, and optimize allocation
            </p>
          </div>
          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
            <h3 className="text-lg font-semibold mb-2">🔐 Privacy First</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Self-hosted, open-source, complete control over your data
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}
