'use client'

import { useState, useEffect } from 'react'
import AppLayout from '@/components/layout/AppLayout'
import CashflowChart from '@/components/reports/CashflowChart'
import SpendingByCategoryChart from '@/components/reports/SpendingByCategoryChart'
import IncomeVsExpensesChart from '@/components/reports/IncomeVsExpensesChart'
import NetWorthChartReport from '@/components/reports/NetWorthChartReport'
import ExportReports from '@/components/reports/ExportReports'
import reportsService, {
  CashflowReport,
  SpendingReport,
  IncomeReport,
  NetWorthReport,
} from '@/lib/reports'

export default function ReportsPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [dateRange, setDateRange] = useState({
    startDate: '',
    endDate: '',
  })
  const [cashflowData, setCashflowData] = useState<CashflowReport | null>(null)
  const [spendingData, setSpendingData] = useState<SpendingReport | null>(null)
  const [incomeData, setIncomeData] = useState<IncomeReport | null>(null)
  const [netWorthData, setNetWorthData] = useState<NetWorthReport | null>(null)

  // Initialize date range (last 6 months)
  useEffect(() => {
    const end = new Date()
    const start = new Date()
    start.setMonth(start.getMonth() - 6)

    setDateRange({
      startDate: start.toISOString().split('T')[0],
      endDate: end.toISOString().split('T')[0],
    })
  }, [])

  // Fetch reports when date range changes
  useEffect(() => {
    if (!dateRange.startDate || !dateRange.endDate) return

    const fetchReports = async () => {
      setIsLoading(true)
      try {
        const [cashflow, spending, income, netWorth] = await Promise.all([
          reportsService.getCashflow({
            start_date: dateRange.startDate,
            end_date: dateRange.endDate,
          }),
          reportsService.getSpending({
            start_date: dateRange.startDate,
            end_date: dateRange.endDate,
          }),
          reportsService.getIncome({
            start_date: dateRange.startDate,
            end_date: dateRange.endDate,
          }),
          reportsService.getNetWorth({
            start_date: dateRange.startDate,
            end_date: dateRange.endDate,
          }),
        ])

        setCashflowData(cashflow)
        setSpendingData(spending)
        setIncomeData(income)
        setNetWorthData(netWorth)
      } catch (error) {
        console.error('Error fetching reports:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchReports()
  }, [dateRange])

  const handleQuickRange = (months: number) => {
    const end = new Date()
    const start = new Date()
    start.setMonth(start.getMonth() - months)

    setDateRange({
      startDate: start.toISOString().split('T')[0],
      endDate: end.toISOString().split('T')[0],
    })
  }

  const handleYearToDate = () => {
    const end = new Date()
    const start = new Date(end.getFullYear(), 0, 1)

    setDateRange({
      startDate: start.toISOString().split('T')[0],
      endDate: end.toISOString().split('T')[0],
    })
  }

  const handleLastYear = () => {
    const end = new Date()
    end.setFullYear(end.getFullYear() - 1)
    end.setMonth(11)
    end.setDate(31)

    const start = new Date(end.getFullYear(), 0, 1)

    setDateRange({
      startDate: start.toISOString().split('T')[0],
      endDate: end.toISOString().split('T')[0],
    })
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Financial Reports
          </h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Analyze your financial data with detailed reports and charts
          </p>
        </div>

        {/* Date Range Filter */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6 print:hidden">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Report Period
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label
                htmlFor="startDate"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Start Date
              </label>
              <input
                type="date"
                id="startDate"
                value={dateRange.startDate}
                onChange={(e) =>
                  setDateRange({ ...dateRange, startDate: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            <div>
              <label
                htmlFor="endDate"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                End Date
              </label>
              <input
                type="date"
                id="endDate"
                value={dateRange.endDate}
                onChange={(e) =>
                  setDateRange({ ...dateRange, endDate: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>

          {/* Quick Date Range Buttons */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => handleQuickRange(1)}
              className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200"
            >
              Last Month
            </button>
            <button
              onClick={() => handleQuickRange(3)}
              className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200"
            >
              Last 3 Months
            </button>
            <button
              onClick={() => handleQuickRange(6)}
              className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200"
            >
              Last 6 Months
            </button>
            <button
              onClick={() => handleQuickRange(12)}
              className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200"
            >
              Last 12 Months
            </button>
            <button
              onClick={handleYearToDate}
              className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200"
            >
              Year to Date
            </button>
            <button
              onClick={handleLastYear}
              className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200"
            >
              Last Year
            </button>
          </div>
        </div>

        {/* Export Section */}
        <ExportReports
          cashflowData={cashflowData}
          spendingData={spendingData}
          incomeData={incomeData}
          netWorthData={netWorthData}
          dateRange={dateRange}
        />

        {/* Reports Grid */}
        <div className="space-y-6">
          {/* Cashflow Chart */}
          <CashflowChart data={cashflowData} isLoading={isLoading} />

          {/* Income vs Expenses */}
          <IncomeVsExpensesChart data={cashflowData} isLoading={isLoading} />

          {/* Two Column Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Spending by Category */}
            <SpendingByCategoryChart data={spendingData} isLoading={isLoading} />

            {/* Income Sources - Similar component to Spending */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Income by Source
              </h3>
              {isLoading ? (
                <div className="animate-pulse h-64 bg-gray-200 dark:bg-gray-700 rounded"></div>
              ) : incomeData && incomeData.sources.length > 0 ? (
                <div className="space-y-3">
                  <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 mb-4">
                    <p className="text-xs text-green-600 dark:text-green-400 font-medium">
                      Total Income
                    </p>
                    <p className="text-lg font-bold text-green-700 dark:text-green-300 mt-1">
                      {new Intl.NumberFormat('en-US', {
                        style: 'currency',
                        currency: incomeData.currency,
                      }).format(incomeData.total_income)}
                    </p>
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1">
                      Avg Monthly:{' '}
                      {new Intl.NumberFormat('en-US', {
                        style: 'currency',
                        currency: incomeData.currency,
                      }).format(incomeData.average_monthly_income)}
                    </p>
                  </div>
                  {incomeData.sources.map((source, index) => (
                    <div
                      key={source.category_id || index}
                      className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50"
                    >
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {source.category_name}
                      </span>
                      <div className="text-right">
                        <p className="text-sm font-semibold text-gray-900 dark:text-white">
                          {new Intl.NumberFormat('en-US', {
                            style: 'currency',
                            currency: incomeData.currency,
                          }).format(source.total_amount)}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {source.percentage.toFixed(1)}%
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-8">
                  No income data available
                </p>
              )}
            </div>
          </div>

          {/* Net Worth Timeline */}
          <NetWorthChartReport data={netWorthData} isLoading={isLoading} />
        </div>
      </div>
    </AppLayout>
  )
}
