'use client'

import { useState, useEffect, useCallback } from 'react'
import { useParams, useRouter } from 'next/navigation'
import AppLayout from '@/components/layout/AppLayout'
import portfolioService, {
  Portfolio,
  PortfolioPerformance,
  Holding,
  PortfolioTransaction,
} from '@/lib/portfolio'
import HoldingsTable from '@/components/portfolio/HoldingsTable'
import AddHoldingForm from '@/components/portfolio/AddHoldingForm'
import TransactionHistory from '@/components/portfolio/TransactionHistory'
import PerformanceCharts from '@/components/portfolio/PerformanceCharts'

export default function PortfolioDetailPage() {
  const params = useParams()
  const router = useRouter()
  const portfolioId = parseInt(params.id as string)

  const [portfolio, setPortfolio] = useState<Portfolio | null>(null)
  const [performance, setPerformance] = useState<PortfolioPerformance | null>(null)
  const [holdings, setHoldings] = useState<Holding[]>([])
  const [transactions, setTransactions] = useState<PortfolioTransaction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showAddHolding, setShowAddHolding] = useState(false)

  const loadPortfolioData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const [portfolioData, performanceData, holdingsData, transactionsData] = await Promise.all([
        portfolioService.getPortfolio(portfolioId),
        portfolioService.getPortfolioPerformance(portfolioId).catch(() => null),
        portfolioService.getHoldings(portfolioId),
        portfolioService.getTransactions(portfolioId),
      ])

      setPortfolio(portfolioData)
      setPerformance(performanceData)
      setHoldings(holdingsData)
      setTransactions(transactionsData)
    } catch (err: any) {
      setError(err.message || 'Failed to load portfolio data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }, [portfolioId])

  useEffect(() => {
    if (portfolioId) {
      loadPortfolioData()
    }
  }, [portfolioId, loadPortfolioData])

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount)
  }

  const formatPercentage = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
          <p className="text-gray-500 dark:text-gray-400">Loading portfolio...</p>
        </div>
      </AppLayout>
    )
  }

  if (error || !portfolio) {
    return (
      <AppLayout>
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-800 dark:text-red-200">{error || 'Portfolio not found'}</p>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <button
                onClick={() => router.push('/portfolio')}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                ← Back
              </button>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                {portfolio.name}
              </h2>
            </div>
            {portfolio.description && (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {portfolio.description}
              </p>
            )}
          </div>
          <button
            onClick={() => setShowAddHolding(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            + Add Holding
          </button>
        </div>

        {/* Performance Metrics */}
        {performance && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-700">
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Total Value</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {formatCurrency(performance.total_value)}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-700">
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Total Gain/Loss</p>
              <p
                className={`text-2xl font-bold ${
                  performance.total_gain_loss >= 0
                    ? 'text-green-600 dark:text-green-400'
                    : 'text-red-600 dark:text-red-400'
                }`}
              >
                {formatCurrency(performance.total_gain_loss)}
              </p>
              <p
                className={`text-sm ${
                  performance.total_gain_loss_percentage >= 0
                    ? 'text-green-600 dark:text-green-400'
                    : 'text-red-600 dark:text-red-400'
                }`}
              >
                {formatPercentage(performance.total_gain_loss_percentage)}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-700">
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">ROI</p>
              <p
                className={`text-2xl font-bold ${
                  performance.roi >= 0
                    ? 'text-green-600 dark:text-green-400'
                    : 'text-red-600 dark:text-red-400'
                }`}
              >
                {formatPercentage(performance.roi)}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-700">
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Total Cost</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {formatCurrency(performance.total_cost)}
              </p>
            </div>
          </div>
        )}

        {/* Performance Charts */}
        {performance && <PerformanceCharts performance={performance} portfolioId={portfolioId} />}

        {/* Holdings Table */}
        <div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Holdings</h3>
          <HoldingsTable holdings={holdings} onUpdate={loadPortfolioData} />
        </div>

        {/* Transaction History */}
        <div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Recent Transactions
          </h3>
          <TransactionHistory
            transactions={transactions}
            portfolioId={portfolioId}
            onUpdate={loadPortfolioData}
          />
        </div>

        {/* Add Holding Modal */}
        {showAddHolding && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">Add Holding</h3>
                <button
                  onClick={() => setShowAddHolding(false)}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  ✕
                </button>
              </div>
              <AddHoldingForm
                portfolioId={portfolioId}
                onSuccess={() => {
                  setShowAddHolding(false)
                  loadPortfolioData()
                }}
                onCancel={() => setShowAddHolding(false)}
              />
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  )
}
