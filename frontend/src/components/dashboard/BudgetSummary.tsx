import React from 'react'
import { Budget } from '@/lib/budget'

export interface BudgetSummaryProps {
  budgets: Budget[]
  isLoading?: boolean
}

export default function BudgetSummary({ budgets, isLoading = false }: BudgetSummaryProps) {
  // Ensure budgets is always an array
  const budgetList = Array.isArray(budgets) ? budgets : []

  const formatAmount = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'decimal',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount)
  }

  const getProgressColor = (percentage: number): string => {
    if (percentage >= 90) return 'bg-red-600 dark:bg-red-400'
    if (percentage >= 75) return 'bg-orange-600 dark:bg-orange-400'
    return 'bg-green-600 dark:bg-green-400'
  }

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Budget Overview</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="flex items-center justify-between mb-1">
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-32"></div>
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24"></div>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (budgetList.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Budget Overview</h3>
        </div>
        <div className="p-6">
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
            No budgets configured yet
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Budget Overview</h3>
      </div>
      <div className="p-6">
        <div className="space-y-4">
          {budgetList.slice(0, 5).map((budget) => {
            const spent = budget.spent || 0
            const percentage = (spent / budget.amount) * 100
            const progressColor = getProgressColor(percentage)

            return (
              <div key={budget.id}>
                <div className="flex items-center justify-between mb-1">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {budget.category?.name || 'Uncategorized'}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {formatAmount(spent)} / {formatAmount(budget.amount)}
                  </p>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className={`${progressColor} h-2 rounded-full transition-all`}
                    style={{ width: `${Math.min(percentage, 100)}%` }}
                  />
                </div>
                {percentage >= 100 && (
                  <p className="text-xs text-red-600 dark:text-red-400 mt-1">Over budget!</p>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
