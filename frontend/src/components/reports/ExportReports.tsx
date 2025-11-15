'use client'

import React, { useState } from 'react'
import {
  CashflowReport,
  SpendingReport,
  IncomeReport,
  NetWorthReport,
} from '@/lib/reports'

export interface ExportReportsProps {
  cashflowData: CashflowReport | null
  spendingData: SpendingReport | null
  incomeData: IncomeReport | null
  netWorthData: NetWorthReport | null
  dateRange: {
    startDate: string
    endDate: string
  }
}

export default function ExportReports({
  cashflowData,
  spendingData,
  incomeData,
  netWorthData,
  dateRange,
}: ExportReportsProps) {
  const [isExporting, setIsExporting] = useState(false)

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const exportToCSV = () => {
    setIsExporting(true)
    try {
      let csvContent = 'FinCloud Financial Report\n'
      csvContent += `Report Period: ${formatDate(dateRange.startDate)} - ${formatDate(dateRange.endDate)}\n`
      csvContent += `Generated: ${new Date().toLocaleString()}\n\n`

      // Cashflow Report
      if (cashflowData && cashflowData.data.length > 0) {
        csvContent += '=== CASHFLOW REPORT ===\n'
        csvContent += 'Month,Income,Expenses,Net Cashflow\n'
        cashflowData.data.forEach((row) => {
          csvContent += `${row.month},${row.income},${row.expenses},${row.net}\n`
        })
        csvContent += `\nTotals,${cashflowData.total_income},${cashflowData.total_expenses},${cashflowData.net_cashflow}\n\n`
      }

      // Spending Report
      if (spendingData && spendingData.categories.length > 0) {
        csvContent += '=== SPENDING BY CATEGORY ===\n'
        csvContent += 'Category,Amount,Transactions,Percentage\n'
        spendingData.categories.forEach((cat) => {
          csvContent += `${cat.category_name},${cat.total_amount},${cat.transaction_count},${cat.percentage}%\n`
        })
        csvContent += `\nTotal,${spendingData.total_spending},${spendingData.total_transactions},100%\n\n`
      }

      // Income Report
      if (incomeData && incomeData.sources.length > 0) {
        csvContent += '=== INCOME BY SOURCE ===\n'
        csvContent += 'Source,Amount,Transactions,Percentage\n'
        incomeData.sources.forEach((source) => {
          csvContent += `${source.category_name},${source.total_amount},${source.transaction_count},${source.percentage}%\n`
        })
        csvContent += `\nTotal,${incomeData.total_income},${incomeData.total_transactions},100%\n`
        csvContent += `Average Monthly Income,${incomeData.average_monthly_income}\n\n`
      }

      // Net Worth Report
      if (netWorthData && netWorthData.timeline.length > 0) {
        csvContent += '=== NET WORTH TIMELINE ===\n'
        csvContent += 'Date,Assets,Liabilities,Net Worth\n'
        netWorthData.timeline.forEach((point) => {
          csvContent += `${point.date},${point.total_assets},${point.total_liabilities},${point.net_worth}\n`
        })
        csvContent += `\nCurrent Net Worth,${netWorthData.current_net_worth}\n`
        csvContent += `Change,${netWorthData.change}\n`
        csvContent += `Change Percentage,${netWorthData.change_percentage}%\n\n`

        if (netWorthData.accounts.length > 0) {
          csvContent += '=== ACCOUNT BALANCES ===\n'
          csvContent += 'Account,Type,Balance\n'
          netWorthData.accounts.forEach((acc) => {
            csvContent += `${acc.account_name},${acc.account_type},${acc.balance}\n`
          })
        }
      }

      // Create download link
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute(
        'download',
        `fincloud-report-${dateRange.startDate}-to-${dateRange.endDate}.csv`
      )
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (error) {
      console.error('Error exporting CSV:', error)
      alert('Failed to export CSV. Please try again.')
    } finally {
      setIsExporting(false)
    }
  }

  const exportToPDF = () => {
    setIsExporting(true)
    try {
      // Use browser's print functionality to save as PDF
      window.print()
    } catch (error) {
      console.error('Error exporting PDF:', error)
      alert('Failed to export PDF. Please try again.')
    } finally {
      setIsExporting(false)
    }
  }

  const hasData =
    (cashflowData && cashflowData.data.length > 0) ||
    (spendingData && spendingData.categories.length > 0) ||
    (incomeData && incomeData.sources.length > 0) ||
    (netWorthData && netWorthData.timeline.length > 0)

  if (!hasData) {
    return null
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6 print:hidden">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Export Reports
      </h3>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
        Download your financial reports in various formats
      </p>

      <div className="flex gap-3">
        <button
          onClick={exportToCSV}
          disabled={isExporting}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg
            className="w-5 h-5 mr-2"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          {isExporting ? 'Exporting...' : 'Export to CSV'}
        </button>

        <button
          onClick={exportToPDF}
          disabled={isExporting}
          className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md shadow-sm text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg
            className="w-5 h-5 mr-2"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
            />
          </svg>
          {isExporting ? 'Exporting...' : 'Export to PDF'}
        </button>
      </div>

      <p className="text-xs text-gray-500 dark:text-gray-400 mt-3">
        <strong>CSV:</strong> Download raw data for use in Excel or other spreadsheet applications.
        <br />
        <strong>PDF:</strong> Print-friendly version using your browser's print dialog (Ctrl/Cmd + P → Save as PDF).
      </p>
    </div>
  )
}
