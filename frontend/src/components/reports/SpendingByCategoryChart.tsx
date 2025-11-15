'use client'

import React from 'react'
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts'
import { SpendingReport } from '@/lib/reports'

export interface SpendingByCategoryChartProps {
  data: SpendingReport | null
  isLoading?: boolean
}

const COLORS = [
  '#3b82f6', // blue
  '#10b981', // green
  '#f59e0b', // amber
  '#ef4444', // red
  '#8b5cf6', // purple
  '#ec4899', // pink
  '#06b6d4', // cyan
  '#f97316', // orange
  '#14b8a6', // teal
  '#a855f7', // violet
  '#6366f1', // indigo
  '#84cc16', // lime
]

export default function SpendingByCategoryChart({
  data,
  isLoading = false,
}: SpendingByCategoryChartProps) {
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: data?.currency || 'USD',
      minimumFractionDigits: 0,
    }).format(value)
  }

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Spending by Category
          </h3>
        </div>
        <div className="p-6">
          <div className="animate-pulse h-96 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
      </div>
    )
  }

  if (!data || data.categories.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Spending by Category
          </h3>
        </div>
        <div className="p-6">
          <div className="h-96 flex items-center justify-center">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              No spending data available for the selected period
            </p>
          </div>
        </div>
      </div>
    )
  }

  // Prepare data for pie chart
  const chartData = data.categories.map((cat) => ({
    name: cat.category_name,
    value: cat.total_amount,
    percentage: cat.percentage,
    count: cat.transaction_count,
  }))

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
          <p className="font-semibold text-gray-900 dark:text-white">
            {payload[0].name}
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Amount: {formatCurrency(payload[0].value)}
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Percentage: {payload[0].payload.percentage.toFixed(1)}%
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Transactions: {payload[0].payload.count}
          </p>
        </div>
      )
    }
    return null
  }

  const renderCustomLabel = ({
    cx,
    cy,
    midAngle,
    innerRadius,
    outerRadius,
    percent,
  }: any) => {
    const RADIAN = Math.PI / 180
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5
    const x = cx + radius * Math.cos(-midAngle * RADIAN)
    const y = cy + radius * Math.sin(-midAngle * RADIAN)

    // Only show label if percentage is > 5%
    if (percent < 0.05) return null

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        className="text-xs font-semibold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Spending by Category
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Distribution of expenses across categories
        </p>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 gap-4 mt-4">
          <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
            <p className="text-xs text-gray-600 dark:text-gray-400 font-medium">
              Total Spending
            </p>
            <p className="text-lg font-bold text-gray-900 dark:text-white mt-1">
              {formatCurrency(data.total_spending)}
            </p>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
            <p className="text-xs text-gray-600 dark:text-gray-400 font-medium">
              Total Transactions
            </p>
            <p className="text-lg font-bold text-gray-900 dark:text-white mt-1">
              {data.total_transactions}
            </p>
          </div>
        </div>
      </div>
      <div className="p-6">
        <ResponsiveContainer width="100%" height={400}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={renderCustomLabel}
              outerRadius={120}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend
              layout="vertical"
              align="right"
              verticalAlign="middle"
              formatter={(value, entry: any) => (
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  {value}
                </span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>

        {/* Category List */}
        <div className="mt-6">
          <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
            Category Breakdown
          </h4>
          <div className="space-y-2">
            {data.categories.slice(0, 5).map((category, index) => (
              <div
                key={category.category_id || index}
                className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50"
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: COLORS[index % COLORS.length] }}
                  />
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {category.category_name}
                  </span>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">
                    {formatCurrency(category.total_amount)}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {category.percentage.toFixed(1)}% · {category.transaction_count} txns
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
