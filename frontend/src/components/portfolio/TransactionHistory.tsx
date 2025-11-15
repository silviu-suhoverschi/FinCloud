'use client'

import { useState } from 'react'
import { PortfolioTransaction } from '@/lib/portfolio'
import portfolioService from '@/lib/portfolio'

interface TransactionHistoryProps {
  transactions: PortfolioTransaction[]
  portfolioId: number
  onUpdate: () => void
}

export default function TransactionHistory({
  transactions,
  portfolioId,
  onUpdate,
}: TransactionHistoryProps) {
  const [showAll, setShowAll] = useState(false)

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount)
  }

  const getTransactionTypeColor = (type: string) => {
    switch (type) {
      case 'BUY':
        return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
      case 'SELL':
        return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300'
      case 'DIVIDEND':
        return 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300'
      case 'SPLIT':
        return 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300'
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this transaction?')) return

    try {
      await portfolioService.deleteTransaction(id)
      onUpdate()
    } catch (err) {
      alert('Failed to delete transaction')
      console.error(err)
    }
  }

  const displayTransactions = showAll ? transactions : transactions.slice(0, 10)

  if (transactions.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center border border-gray-200 dark:border-gray-700">
        <p className="text-gray-500 dark:text-gray-400">No transactions yet</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Asset
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Quantity
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Price
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Total
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Notes
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {displayTransactions.map((transaction) => {
                const total = transaction.quantity * transaction.price
                return (
                  <tr key={transaction.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-white whitespace-nowrap">
                      {new Date(transaction.date).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">
                        {transaction.asset?.symbol || 'N/A'}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getTransactionTypeColor(
                          transaction.transaction_type
                        )}`}
                      >
                        {transaction.transaction_type}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right text-sm text-gray-900 dark:text-white">
                      {transaction.quantity.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-right text-sm text-gray-900 dark:text-white">
                      {formatCurrency(transaction.price)}
                    </td>
                    <td className="px-4 py-3 text-right text-sm font-medium text-gray-900 dark:text-white">
                      {formatCurrency(total)}
                      {transaction.fee && transaction.fee > 0 && (
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          Fee: {formatCurrency(transaction.fee)}
                        </div>
                      )}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400 max-w-xs truncate">
                      {transaction.notes || '-'}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => handleDelete(transaction.id)}
                        className="text-red-600 dark:text-red-400 hover:underline text-sm"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {transactions.length > 10 && (
        <div className="text-center">
          <button
            onClick={() => setShowAll(!showAll)}
            className="px-4 py-2 text-blue-600 dark:text-blue-400 hover:underline text-sm font-medium"
          >
            {showAll ? 'Show Less' : `Show All ${transactions.length} Transactions`}
          </button>
        </div>
      )}
    </div>
  )
}
