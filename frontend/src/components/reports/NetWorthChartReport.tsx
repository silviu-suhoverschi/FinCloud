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
  Line,
} from 'recharts'
import { NetWorthReport } from '@/lib/reports'

export interface NetWorthChartReportProps {
  data: NetWorthReport | null
  isLoading?: boolean
}

export default function NetWorthChartReport({
  data,
  isLoading = false,
}: NetWorthChartReportProps) {
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: data?.currency || 'USD',
      minimumFractionDigits: 0,
    }).format(value)
  }

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
  }

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Net Worth Timeline
          </h3>
        </div>
        <div className="p-6">
          <div className="animate-pulse h-96 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
      </div>
    )
  }

  if (!data || data.timeline.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Net Worth Timeline
          </h3>
        </div>
        <div className="p-6">
          <div className="h-96 flex items-center justify-center">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              No net worth data available
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Net Worth Timeline
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Track your assets, liabilities, and net worth over time
        </p>

        {/* Summary Stats */}
        <div className="grid grid-cols-3 gap-4 mt-4">
          <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3">
            <p className="text-xs text-purple-600 dark:text-purple-400 font-medium">
              Current Net Worth
            </p>
            <p className="text-lg font-bold text-purple-700 dark:text-purple-300 mt-1">
              {formatCurrency(data.current_net_worth)}
            </p>
          </div>
          <div className={`${data.change >= 0 ? 'bg-green-50 dark:bg-green-900/20' : 'bg-red-50 dark:bg-red-900/20'} rounded-lg p-3`}>
            <p className={`text-xs ${data.change >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'} font-medium`}>
              Change
            </p>
            <p className={`text-lg font-bold ${data.change >= 0 ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300'} mt-1`}>
              {formatCurrency(data.change)}
            </p>
          </div>
          <div className={`${data.change_percentage >= 0 ? 'bg-blue-50 dark:bg-blue-900/20' : 'bg-orange-50 dark:bg-orange-900/20'} rounded-lg p-3`}>
            <p className={`text-xs ${data.change_percentage >= 0 ? 'text-blue-600 dark:text-blue-400' : 'text-orange-600 dark:text-orange-400'} font-medium`}>
              Growth Rate
            </p>
            <p className={`text-lg font-bold ${data.change_percentage >= 0 ? 'text-blue-700 dark:text-blue-300' : 'text-orange-700 dark:text-orange-300'} mt-1`}>
              {data.change_percentage >= 0 ? '+' : ''}
              {data.change_percentage.toFixed(2)}%
            </p>
          </div>
        </div>
      </div>
      <div className="p-6">
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={data.timeline}>
            <defs>
              <linearGradient id="colorAssetsReport" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.1} />
              </linearGradient>
              <linearGradient id="colorLiabilitiesReport" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1} />
              </linearGradient>
              <linearGradient id="colorNetWorthReport" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
            <XAxis
              dataKey="date"
              tickFormatter={formatDate}
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
              labelFormatter={formatDate}
              formatter={(value: number) => formatCurrency(value)}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="total_assets"
              stroke="#10b981"
              fillOpacity={1}
              fill="url(#colorAssetsReport)"
              name="Assets"
            />
            <Area
              type="monotone"
              dataKey="total_liabilities"
              stroke="#ef4444"
              fillOpacity={1}
              fill="url(#colorLiabilitiesReport)"
              name="Liabilities"
            />
            <Line
              type="monotone"
              dataKey="net_worth"
              stroke="#8b5cf6"
              strokeWidth={3}
              dot={false}
              name="Net Worth"
              activeDot={{ r: 6 }}
            />
          </AreaChart>
        </ResponsiveContainer>

        {/* Account Balances */}
        {data.accounts && data.accounts.length > 0 && (
          <div className="mt-6">
            <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
              Current Account Balances
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {data.accounts.map((account) => (
                <div
                  key={account.account_id}
                  className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {account.account_name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {account.account_type}
                    </p>
                  </div>
                  <p
                    className={`text-sm font-bold ${
                      account.balance >= 0
                        ? 'text-green-600 dark:text-green-400'
                        : 'text-red-600 dark:text-red-400'
                    }`}
                  >
                    {formatCurrency(account.balance)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
