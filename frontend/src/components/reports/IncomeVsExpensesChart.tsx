'use client'

import React from 'react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { CashflowReport } from '@/lib/reports'

export interface IncomeVsExpensesChartProps {
  data: CashflowReport | null
  isLoading?: boolean
}

export default function IncomeVsExpensesChart({
  data,
  isLoading = false,
}: IncomeVsExpensesChartProps) {
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: data?.currency || 'USD',
      minimumFractionDigits: 0,
    }).format(value)
  }

  const formatMonth = (month: string): string => {
    const [year, monthNum] = month.split('-')
    const date = new Date(parseInt(year), parseInt(monthNum) - 1)
    return date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' })
  }

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Income vs Expenses Timeline
          </h3>
        </div>
        <div className="p-6">
          <div className="animate-pulse h-80 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
      </div>
    )
  }

  if (!data || data.data.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Income vs Expenses Timeline
          </h3>
        </div>
        <div className="p-6">
          <div className="h-80 flex items-center justify-center">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              No data available for the selected period
            </p>
          </div>
        </div>
      </div>
    )
  }

  // Calculate savings rate for each month
  const chartData = data.data.map((point) => ({
    ...point,
    savingsRate: point.income > 0 ? ((point.income - point.expenses) / point.income) * 100 : 0,
  }))

  const avgSavingsRate =
    data.total_income > 0
      ? ((data.total_income - data.total_expenses) / data.total_income) * 100
      : 0

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Income vs Expenses Timeline
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Track your income and expenses over time
        </p>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 gap-4 mt-4">
          <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
            <p className="text-xs text-gray-600 dark:text-gray-400 font-medium">
              Average Monthly Income
            </p>
            <p className="text-lg font-bold text-gray-900 dark:text-white mt-1">
              {formatCurrency(data.total_income / data.data.length)}
            </p>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
            <p className="text-xs text-gray-600 dark:text-gray-400 font-medium">
              Average Savings Rate
            </p>
            <p
              className={`text-lg font-bold mt-1 ${
                avgSavingsRate >= 20
                  ? 'text-green-600 dark:text-green-400'
                  : avgSavingsRate >= 10
                  ? 'text-yellow-600 dark:text-yellow-400'
                  : 'text-red-600 dark:text-red-400'
              }`}
            >
              {avgSavingsRate.toFixed(1)}%
            </p>
          </div>
        </div>
      </div>
      <div className="p-6">
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorIncomeArea" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.1} />
              </linearGradient>
              <linearGradient id="colorExpensesArea" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
            <XAxis
              dataKey="month"
              tickFormatter={formatMonth}
              className="text-xs text-gray-600 dark:text-gray-400"
              stroke="currentColor"
            />
            <YAxis
              tickFormatter={formatCurrency}
              className="text-xs text-gray-600 dark:text-gray-400"
              stroke="currentColor"
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                border: '1px solid #e5e7eb',
                borderRadius: '0.5rem',
              }}
              labelFormatter={formatMonth}
              formatter={(value: number, name: string) => {
                if (name === 'savingsRate') {
                  return [`${value.toFixed(1)}%`, 'Savings Rate']
                }
                return [formatCurrency(value), name]
              }}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="income"
              stroke="#10b981"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorIncomeArea)"
              name="Income"
            />
            <Area
              type="monotone"
              dataKey="expenses"
              stroke="#ef4444"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorExpensesArea)"
              name="Expenses"
            />
          </AreaChart>
        </ResponsiveContainer>

        {/* Monthly breakdown table */}
        <div className="mt-6">
          <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
            Monthly Breakdown
          </h4>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700/50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Month
                  </th>
                  <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Income
                  </th>
                  <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Expenses
                  </th>
                  <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Net
                  </th>
                  <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Savings Rate
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {chartData.slice(-6).reverse().map((row, index) => (
                  <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {formatMonth(row.month)}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-right text-green-600 dark:text-green-400 font-medium">
                      {formatCurrency(row.income)}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-right text-red-600 dark:text-red-400 font-medium">
                      {formatCurrency(row.expenses)}
                    </td>
                    <td className={`px-4 py-2 whitespace-nowrap text-sm text-right font-medium ${row.net >= 0 ? 'text-blue-600 dark:text-blue-400' : 'text-orange-600 dark:text-orange-400'}`}>
                      {formatCurrency(row.net)}
                    </td>
                    <td className={`px-4 py-2 whitespace-nowrap text-sm text-right font-medium ${row.savingsRate >= 20 ? 'text-green-600 dark:text-green-400' : row.savingsRate >= 10 ? 'text-yellow-600 dark:text-yellow-400' : 'text-red-600 dark:text-red-400'}`}>
                      {row.savingsRate.toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
