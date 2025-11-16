import React from 'react'

export interface MetricCardProps {
  title: string
  value: string | number
  icon: React.ReactNode
  iconColor: 'blue' | 'green' | 'orange' | 'purple' | 'red'
  subtitle?: string
  trend?: {
    value: number
    label: string
    isPositive?: boolean
  }
  isLoading?: boolean
}

const colorClasses = {
  blue: {
    bg: 'bg-blue-100 dark:bg-blue-900/20',
    text: 'text-blue-600 dark:text-blue-400',
  },
  green: {
    bg: 'bg-green-100 dark:bg-green-900/20',
    text: 'text-green-600 dark:text-green-400',
  },
  orange: {
    bg: 'bg-orange-100 dark:bg-orange-900/20',
    text: 'text-orange-600 dark:text-orange-400',
  },
  purple: {
    bg: 'bg-purple-100 dark:bg-purple-900/20',
    text: 'text-purple-600 dark:text-purple-400',
  },
  red: {
    bg: 'bg-red-100 dark:bg-red-900/20',
    text: 'text-red-600 dark:text-red-400',
  },
}

export default function MetricCard({
  title,
  value,
  icon,
  iconColor,
  subtitle,
  trend,
  isLoading = false,
}: MetricCardProps) {
  const colors = colorClasses[iconColor]

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <div className="animate-pulse">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24 mb-2"></div>
              <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-32 mt-2"></div>
            </div>
            <div className="w-12 h-12 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
          </div>
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-20 mt-2"></div>
        </div>
      </div>
    )
  }

  const formatValue = (val: string | number): string => {
    if (typeof val === 'number') {
      return new Intl.NumberFormat('en-US', {
        style: 'decimal',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(val)
    }
    return val
  }

  const trendColor = trend?.isPositive !== false ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
            {formatValue(value)}
          </p>
        </div>
        <div className={`w-12 h-12 ${colors.bg} rounded-full flex items-center justify-center`}>
          <div className={colors.text}>{icon}</div>
        </div>
      </div>
      {(subtitle || trend) && (
        <div className="mt-2">
          {trend && (
            <p className={`text-xs ${trendColor}`}>
              {trend.value > 0 ? '+' : ''}
              {trend.value.toFixed(1)}% {trend.label}
            </p>
          )}
          {subtitle && !trend && (
            <p className="text-xs text-gray-600 dark:text-gray-400">{subtitle}</p>
          )}
        </div>
      )}
    </div>
  )
}
