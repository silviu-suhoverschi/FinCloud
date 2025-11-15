'use client'

import { useEffect, useState } from 'react'
import AppLayout from '@/components/layout/AppLayout'
import MetricCard from '@/components/dashboard/MetricCard'
import RecentTransactions from '@/components/dashboard/RecentTransactions'
import BudgetSummary from '@/components/dashboard/BudgetSummary'
import PortfolioValueChart from '@/components/dashboard/PortfolioValueChart'
import NetWorthChart from '@/components/dashboard/NetWorthChart'
import dashboardService, { DashboardMetrics } from '@/lib/dashboard'
import budgetService, { Transaction, Budget } from '@/lib/budget'
import portfolioService, { PortfolioValueHistory } from '@/lib/portfolio'
import reportsService, { NetWorthDataPointLegacy } from '@/lib/reports'

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([])
  const [budgets, setBudgets] = useState<Budget[]>([])
  const [portfolioHistory, setPortfolioHistory] = useState<PortfolioValueHistory[]>([])
  const [netWorthHistory, setNetWorthHistory] = useState<NetWorthDataPointLegacy[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true)

        // Fetch all data in parallel
        const [metricsData, transactions, budgetsData, netWorth] = await Promise.all([
          dashboardService.getMetrics(),
          budgetService.getRecentTransactions(5),
          budgetService.getBudgets(),
          reportsService.getNetWorthLegacy({ interval: 'monthly' }),
        ])

        setMetrics(metricsData)
        setRecentTransactions(transactions)
        setBudgets(budgetsData)
        setNetWorthHistory(netWorth)

        // Fetch portfolio history if there are portfolios
        try {
          const portfolios = await portfolioService.getPortfolios()
          if (portfolios.length > 0) {
            const history = await portfolioService.getPortfolioValueHistory(portfolios[0].id, 30)
            setPortfolioHistory(history)
          }
        } catch (error) {
          console.error('Error fetching portfolio history:', error)
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Page header */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Welcome to FinCloud
          </h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Your financial overview at a glance
          </p>
        </div>

        {/* Stats grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Total Balance"
            value={metrics?.totalBalance || 0}
            icon={
              <svg
                className="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
                />
              </svg>
            }
            iconColor="blue"
            trend={
              metrics?.balanceChange
                ? {
                    value: metrics.balanceChange,
                    label: 'from last month',
                    isPositive: metrics.balanceChange > 0,
                  }
                : undefined
            }
            isLoading={isLoading}
          />

          <MetricCard
            title="Portfolio Value"
            value={metrics?.portfolioValue || 0}
            icon={
              <svg
                className="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                />
              </svg>
            }
            iconColor="green"
            trend={
              metrics?.portfolioROI
                ? {
                    value: metrics.portfolioROI,
                    label: 'ROI',
                    isPositive: metrics.portfolioROI > 0,
                  }
                : undefined
            }
            isLoading={isLoading}
          />

          <MetricCard
            title="Monthly Spending"
            value={metrics?.monthlySpending || 0}
            icon={
              <svg
                className="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            }
            iconColor="orange"
            subtitle={
              metrics?.budgetUsage
                ? `${metrics.budgetUsage.toFixed(0)}% of budget`
                : undefined
            }
            isLoading={isLoading}
          />

          <MetricCard
            title="Net Worth"
            value={metrics?.netWorth || 0}
            icon={
              <svg
                className="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            }
            iconColor="purple"
            trend={
              metrics?.netWorthChange
                ? {
                    value: metrics.netWorthChange,
                    label: 'YTD',
                    isPositive: metrics.netWorthChange > 0,
                  }
                : undefined
            }
            isLoading={isLoading}
          />
        </div>

        {/* Recent activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <RecentTransactions transactions={recentTransactions} isLoading={isLoading} />
          <BudgetSummary budgets={budgets} isLoading={isLoading} />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PortfolioValueChart data={portfolioHistory} isLoading={isLoading} />
          <NetWorthChart data={netWorthHistory} isLoading={isLoading} />
        </div>
      </div>
    </AppLayout>
  )
}
