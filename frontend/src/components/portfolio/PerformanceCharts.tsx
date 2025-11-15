'use client'

import { useState, useEffect } from 'react'
import { PortfolioPerformance, PortfolioValueHistory } from '@/lib/portfolio'
import portfolioService from '@/lib/portfolio'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { Line, Pie } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface PerformanceChartsProps {
  performance: PortfolioPerformance
  portfolioId: number
}

export default function PerformanceCharts({ performance, portfolioId }: PerformanceChartsProps) {
  const [valueHistory, setValueHistory] = useState<PortfolioValueHistory[]>([])
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState<'7' | '30' | '90' | '365'>('30')

  useEffect(() => {
    loadValueHistory()
  }, [portfolioId, timeRange])

  const loadValueHistory = async () => {
    try {
      setLoading(true)
      const history = await portfolioService.getPortfolioValueHistory(
        portfolioId,
        parseInt(timeRange)
      )
      setValueHistory(history)
    } catch (err) {
      console.error('Failed to load value history:', err)
      setValueHistory([])
    } finally {
      setLoading(false)
    }
  }

  // Portfolio Value Chart Data
  const valueChartData = {
    labels: valueHistory.map((item) => new Date(item.date).toLocaleDateString()),
    datasets: [
      {
        label: 'Portfolio Value',
        data: valueHistory.map((item) => item.value),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  }

  const valueChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: function (context: any) {
            return new Intl.NumberFormat('en-US', {
              style: 'currency',
              currency: 'USD',
            }).format(context.parsed.y)
          },
        },
      },
    },
    scales: {
      y: {
        ticks: {
          callback: function (value: any) {
            return new Intl.NumberFormat('en-US', {
              style: 'currency',
              currency: 'USD',
              notation: 'compact',
            }).format(value)
          },
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
      },
      x: {
        grid: {
          display: false,
        },
      },
    },
  }

  // Asset Allocation Pie Chart Data
  const allocationData = {
    labels: performance.asset_allocation.map((item) => item.asset_type.toUpperCase()),
    datasets: [
      {
        data: performance.asset_allocation.map((item) => item.value),
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(249, 115, 22, 0.8)',
          'rgba(139, 92, 246, 0.8)',
          'rgba(236, 72, 153, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(20, 184, 166, 0.8)',
        ],
        borderColor: [
          'rgb(59, 130, 246)',
          'rgb(16, 185, 129)',
          'rgb(249, 115, 22)',
          'rgb(139, 92, 246)',
          'rgb(236, 72, 153)',
          'rgb(245, 158, 11)',
          'rgb(20, 184, 166)',
        ],
        borderWidth: 2,
      },
    ],
  }

  const allocationOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
      },
      tooltip: {
        callbacks: {
          label: function (context: any) {
            const label = context.label || ''
            const value = context.parsed
            const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0)
            const percentage = ((value / total) * 100).toFixed(2)
            const formattedValue = new Intl.NumberFormat('en-US', {
              style: 'currency',
              currency: 'USD',
            }).format(value)
            return `${label}: ${formattedValue} (${percentage}%)`
          },
        },
      },
    },
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Portfolio Value Chart */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Portfolio Value</h3>
          <div className="flex gap-2">
            {(['7', '30', '90', '365'] as const).map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-3 py-1 text-xs rounded-lg transition-colors ${
                  timeRange === range
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                {range === '7' ? '7D' : range === '30' ? '1M' : range === '90' ? '3M' : '1Y'}
              </button>
            ))}
          </div>
        </div>
        {loading ? (
          <div className="h-64 flex items-center justify-center">
            <p className="text-gray-500 dark:text-gray-400">Loading chart...</p>
          </div>
        ) : valueHistory.length > 0 ? (
          <div className="h-64">
            <Line data={valueChartData} options={valueChartOptions} />
          </div>
        ) : (
          <div className="h-64 flex items-center justify-center">
            <p className="text-gray-500 dark:text-gray-400">No data available</p>
          </div>
        )}
      </div>

      {/* Asset Allocation Chart */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Asset Allocation
        </h3>
        {performance.asset_allocation.length > 0 ? (
          <div className="h-64">
            <Pie data={allocationData} options={allocationOptions} />
          </div>
        ) : (
          <div className="h-64 flex items-center justify-center">
            <p className="text-gray-500 dark:text-gray-400">No allocation data</p>
          </div>
        )}
      </div>

      {/* Performance Metrics Details */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700 lg:col-span-2">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Performance Metrics
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {performance.xirr !== undefined && performance.xirr !== null && (
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">XIRR</p>
              <p
                className={`text-xl font-bold ${
                  performance.xirr >= 0
                    ? 'text-green-600 dark:text-green-400'
                    : 'text-red-600 dark:text-red-400'
                }`}
              >
                {performance.xirr >= 0 ? '+' : ''}
                {performance.xirr.toFixed(2)}%
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Extended Internal Rate of Return
              </p>
            </div>
          )}
          {performance.twr !== undefined && performance.twr !== null && (
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">TWR</p>
              <p
                className={`text-xl font-bold ${
                  performance.twr >= 0
                    ? 'text-green-600 dark:text-green-400'
                    : 'text-red-600 dark:text-red-400'
                }`}
              >
                {performance.twr >= 0 ? '+' : ''}
                {performance.twr.toFixed(2)}%
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Time-Weighted Return
              </p>
            </div>
          )}
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Asset Types</p>
            <p className="text-xl font-bold text-gray-900 dark:text-white">
              {performance.asset_allocation.length}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Different asset types</p>
          </div>
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Diversification</p>
            <p className="text-xl font-bold text-gray-900 dark:text-white">
              {performance.asset_allocation.length > 0
                ? (
                    (1 -
                      Math.max(
                        ...performance.asset_allocation.map((a) => a.percentage)
                      ) /
                        100) *
                    100
                  ).toFixed(0)
                : 0}
              %
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Portfolio balance</p>
          </div>
        </div>
      </div>
    </div>
  )
}
