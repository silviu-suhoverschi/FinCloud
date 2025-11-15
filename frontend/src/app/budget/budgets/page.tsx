'use client'

import { useState, useEffect } from 'react'
import AppLayout from '@/components/layout/AppLayout'
import budgetService, { Budget, Category } from '@/lib/budget'
import Link from 'next/link'

export default function BudgetsPage() {
  const [budgets, setBudgets] = useState<Budget[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadBudgets()
  }, [])

  const loadBudgets = async () => {
    try {
      setLoading(true)
      const data = await budgetService.getBudgets()
      setBudgets(data)
      setError(null)
    } catch (err) {
      setError('Failed to load budgets')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteBudget = async (id: number) => {
    if (!confirm('Are you sure you want to delete this budget?')) return

    try {
      await budgetService.deleteBudget(id)
      await loadBudgets()
    } catch (err) {
      alert('Failed to delete budget')
      console.error(err)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount)
  }

  const getProgressColor = (percentage: number) => {
    if (percentage >= 100) return 'bg-red-500'
    if (percentage >= 80) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  const getProgressTextColor = (percentage: number) => {
    if (percentage >= 100) return 'text-red-600 dark:text-red-400'
    if (percentage >= 80) return 'text-yellow-600 dark:text-yellow-400'
    return 'text-green-600 dark:text-green-400'
  }

  const calculatePercentage = (spent: number | undefined, amount: number) => {
    if (!spent) return 0
    return Math.round((spent / amount) * 100)
  }

  // Group budgets by period
  const monthlyBudgets = budgets.filter((b) => b.period === 'monthly')
  const yearlyBudgets = budgets.filter((b) => b.period === 'yearly')

  const BudgetCard = ({ budget }: { budget: Budget }) => {
    const percentage = calculatePercentage(budget.spent, budget.amount)
    const remaining = budget.remaining ?? (budget.amount - (budget.spent ?? 0))

    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {budget.category?.name || 'Uncategorized'}
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 capitalize">
              {budget.period} budget
            </p>
          </div>
          <div className="flex gap-2">
            <Link
              href={`/budget/budgets/${budget.id}/edit`}
              className="text-blue-600 dark:text-blue-400 hover:underline text-sm"
            >
              Edit
            </Link>
            <button
              onClick={() => handleDeleteBudget(budget.id)}
              className="text-red-600 dark:text-red-400 hover:underline text-sm"
            >
              Delete
            </button>
          </div>
        </div>

        <div className="space-y-3">
          {/* Progress Bar */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className={`text-2xl font-bold ${getProgressTextColor(percentage)}`}>
                {percentage}%
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {formatCurrency(budget.spent ?? 0)} / {formatCurrency(budget.amount)}
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
              <div
                className={`h-full ${getProgressColor(percentage)} transition-all duration-300`}
                style={{ width: `${Math.min(percentage, 100)}%` }}
              ></div>
            </div>
          </div>

          {/* Remaining Amount */}
          <div className="flex items-center justify-between pt-3 border-t border-gray-200 dark:border-gray-700">
            <span className="text-sm text-gray-500 dark:text-gray-400">Remaining</span>
            <span className={`text-lg font-semibold ${remaining >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
              {formatCurrency(remaining)}
            </span>
          </div>

          {/* Date Range */}
          {budget.start_date && (
            <div className="text-xs text-gray-500 dark:text-gray-400">
              From {new Date(budget.start_date).toLocaleDateString()}
              {budget.end_date && ` to ${new Date(budget.end_date).toLocaleDateString()}`}
            </div>
          )}
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
              Budgets
            </h2>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Track your spending against budget goals
            </p>
          </div>
          <Link
            href="/budget/budgets/new"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            + New Budget
          </Link>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">Total Budgets</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {budgets.length}
            </p>
          </div>
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg shadow p-4">
            <p className="text-sm text-blue-600 dark:text-blue-400">Monthly Budgets</p>
            <p className="text-2xl font-bold text-blue-700 dark:text-blue-300">
              {monthlyBudgets.length}
            </p>
          </div>
          <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg shadow p-4">
            <p className="text-sm text-purple-600 dark:text-purple-400">Yearly Budgets</p>
            <p className="text-2xl font-bold text-purple-700 dark:text-purple-300">
              {yearlyBudgets.length}
            </p>
          </div>
        </div>

        {/* Loading/Error/Empty States */}
        {loading ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
            <p className="text-gray-500 dark:text-gray-400">Loading budgets...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <p className="text-red-800 dark:text-red-200">{error}</p>
          </div>
        ) : budgets.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
            <p className="text-gray-500 dark:text-gray-400 mb-4">No budgets yet. Create your first budget!</p>
            <Link
              href="/budget/budgets/new"
              className="inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create Budget
            </Link>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Monthly Budgets */}
            {monthlyBudgets.length > 0 && (
              <div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                  Monthly Budgets
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {monthlyBudgets.map((budget) => (
                    <BudgetCard key={budget.id} budget={budget} />
                  ))}
                </div>
              </div>
            )}

            {/* Yearly Budgets */}
            {yearlyBudgets.length > 0 && (
              <div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                  Yearly Budgets
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {yearlyBudgets.map((budget) => (
                    <BudgetCard key={budget.id} budget={budget} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </AppLayout>
  )
}
