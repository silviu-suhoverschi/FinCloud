'use client'

import { useEffect, useState, useCallback } from 'react'
import budgetService, { Budget } from '@/lib/budget'

interface BudgetProgressProps {
  budgetId?: number
  showAll?: boolean
  limit?: number
}

export default function BudgetProgress({ budgetId, showAll = false, limit = 5 }: BudgetProgressProps) {
  const [budgets, setBudgets] = useState<Budget[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadBudgets = useCallback(async () => {
    try {
      setLoading(true)
      if (budgetId) {
        const budget = await budgetService.getBudget(budgetId)
        setBudgets([budget])
      } else {
        const allBudgets = await budgetService.getBudgets()
        setBudgets(showAll ? allBudgets : allBudgets.slice(0, limit))
      }
      setError(null)
    } catch (err) {
      setError('Failed to load budget progress')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }, [budgetId, showAll, limit])

  useEffect(() => {
    loadBudgets()
  }, [loadBudgets])

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount)
  }

  const calculatePercentage = (spent: number | undefined, amount: number) => {
    if (!spent) return 0
    return Math.round((spent / amount) * 100)
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

  const getStatusText = (percentage: number) => {
    if (percentage >= 100) return 'Over budget'
    if (percentage >= 80) return 'Approaching limit'
    return 'On track'
  }

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <p className="text-gray-500 dark:text-gray-400 text-center">Loading budget progress...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <p className="text-red-800 dark:text-red-200">{error}</p>
      </div>
    )
  }

  if (budgets.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <p className="text-gray-500 dark:text-gray-400 text-center">No budgets to display</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {budgets.map((budget) => {
        const percentage = calculatePercentage(budget.spent, budget.amount)
        const remaining = budget.remaining ?? (budget.amount - (budget.spent ?? 0))

        return (
          <div
            key={budget.id}
            className="bg-white dark:bg-gray-800 rounded-lg shadow p-5 hover:shadow-md transition-shadow"
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-3">
              <div>
                <h4 className="text-base font-semibold text-gray-900 dark:text-white">
                  {budget.category?.name || 'Uncategorized'}
                </h4>
                <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                  {budget.period}
                </p>
              </div>
              <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                percentage >= 100
                  ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                  : percentage >= 80
                  ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                  : 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
              }`}>
                {getStatusText(percentage)}
              </span>
            </div>

            {/* Progress Bar */}
            <div className="mb-3">
              <div className="flex items-center justify-between mb-1.5">
                <span className={`text-xl font-bold ${getProgressTextColor(percentage)}`}>
                  {percentage}%
                </span>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {formatCurrency(budget.spent ?? 0)} / {formatCurrency(budget.amount)}
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 overflow-hidden">
                <div
                  className={`h-full ${getProgressColor(percentage)} transition-all duration-500 ease-out`}
                  style={{ width: `${Math.min(percentage, 100)}%` }}
                ></div>
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between pt-3 border-t border-gray-200 dark:border-gray-700">
              <span className="text-xs text-gray-500 dark:text-gray-400">Remaining</span>
              <span className={`text-sm font-semibold ${
                remaining >= 0
                  ? 'text-green-600 dark:text-green-400'
                  : 'text-red-600 dark:text-red-400'
              }`}>
                {formatCurrency(remaining)}
              </span>
            </div>
          </div>
        )
      })}
    </div>
  )
}
