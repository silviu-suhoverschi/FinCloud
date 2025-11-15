'use client'

import { useState, useEffect } from 'react'
import AppLayout from '@/components/layout/AppLayout'
import portfolioService, { Portfolio } from '@/lib/portfolio'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function PortfoliosPage() {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newPortfolio, setNewPortfolio] = useState({ name: '', description: '' })
  const [creating, setCreating] = useState(false)
  const router = useRouter()

  useEffect(() => {
    loadPortfolios()
  }, [])

  const loadPortfolios = async () => {
    try {
      setLoading(true)
      const data = await portfolioService.getPortfolios()
      setPortfolios(data)
      setError(null)
    } catch (err) {
      setError('Failed to load portfolios')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreatePortfolio = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newPortfolio.name.trim()) return

    try {
      setCreating(true)
      await portfolioService.createPortfolio(newPortfolio)
      setNewPortfolio({ name: '', description: '' })
      setShowCreateModal(false)
      await loadPortfolios()
    } catch (err) {
      alert('Failed to create portfolio')
      console.error(err)
    } finally {
      setCreating(false)
    }
  }

  const handleDeletePortfolio = async (id: number) => {
    if (!confirm('Are you sure you want to delete this portfolio? This will also delete all holdings and transactions.')) return

    try {
      await portfolioService.deletePortfolio(id)
      await loadPortfolios()
    } catch (err) {
      alert('Failed to delete portfolio')
      console.error(err)
    }
  }

  const PortfolioCard = ({ portfolio }: { portfolio: Portfolio }) => {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition-shadow border border-gray-200 dark:border-gray-700">
        <div className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-1">
                {portfolio.name}
              </h3>
              {portfolio.description && (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {portfolio.description}
                </p>
              )}
            </div>
          </div>

          <div className="text-xs text-gray-400 dark:text-gray-500 mb-4">
            Created {new Date(portfolio.created_at).toLocaleDateString()}
          </div>

          <div className="flex gap-2">
            <Link
              href={`/portfolio/${portfolio.id}`}
              className="flex-1 px-4 py-2 bg-blue-600 text-white text-center rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
            >
              View Details
            </Link>
            <button
              onClick={() => handleDeletePortfolio(portfolio.id)}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Portfolios
            </h2>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Manage your investment portfolios and track performance
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            + New Portfolio
          </button>
        </div>

        {/* Summary Card */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">Total Portfolios</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {portfolios.length}
            </p>
          </div>
        </div>

        {/* Loading/Error/Empty States */}
        {loading ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
            <p className="text-gray-500 dark:text-gray-400">Loading portfolios...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <p className="text-red-800 dark:text-red-200">{error}</p>
          </div>
        ) : portfolios.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
            <p className="text-gray-500 dark:text-gray-400 mb-4">No portfolios yet. Create your first portfolio!</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create Portfolio
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {portfolios.map((portfolio) => (
              <PortfolioCard key={portfolio.id} portfolio={portfolio} />
            ))}
          </div>
        )}

        {/* Create Portfolio Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-md">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                Create New Portfolio
              </h3>
              <form onSubmit={handleCreatePortfolio} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Portfolio Name *
                  </label>
                  <input
                    type="text"
                    value={newPortfolio.name}
                    onChange={(e) => setNewPortfolio({ ...newPortfolio, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    placeholder="My Portfolio"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Description
                  </label>
                  <textarea
                    value={newPortfolio.description}
                    onChange={(e) => setNewPortfolio({ ...newPortfolio, description: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    placeholder="Portfolio description..."
                    rows={3}
                  />
                </div>
                <div className="flex gap-2 justify-end">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={creating}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                  >
                    {creating ? 'Creating...' : 'Create Portfolio'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  )
}
