'use client'

import { useState, useEffect } from 'react'
import AppLayout from '@/components/layout/AppLayout'
import BudgetProgress from '@/components/budget/BudgetProgress'
import budgetService from '@/lib/budget'
import Link from 'next/link'

export default function BudgetPage() {
  const [stats, setStats] = useState({
    totalBalance: 0,
    accountCount: 0,
    transactionCount: 0,
    budgetCount: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      const [accounts, transactions, budgets] = await Promise.all([
        budgetService.getAccounts(),
        budgetService.getTransactions({ limit: 1000 }),
        budgetService.getBudgets(),
      ])

      const totalBalance = accounts.reduce((sum, acc) => sum + acc.current_balance, 0)

      setStats({
        totalBalance,
        accountCount: accounts.length,
        transactionCount: transactions.length,
        budgetCount: budgets.length,
      })
    } catch (err) {
      console.error('Failed to load stats:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'decimal',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount)
  }

  const navigationCards = [
    {
      title: 'Accounts',
      description: 'Manage your bank accounts, credit cards, and cash',
      href: '/budget/accounts',
      icon: '💳',
      color: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800',
      textColor: 'text-blue-600 dark:text-blue-400',
    },
    {
      title: 'Transactions',
      description: 'View and manage all your financial transactions',
      href: '/budget/transactions',
      icon: '💸',
      color: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800',
      textColor: 'text-green-600 dark:text-green-400',
    },
    {
      title: 'Categories',
      description: 'Organize transactions with custom categories',
      href: '/budget/categories',
      icon: '📁',
      color: 'bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800',
      textColor: 'text-purple-600 dark:text-purple-400',
    },
    {
      title: 'Budgets',
      description: 'Set spending limits and track your budget goals',
      href: '/budget/budgets',
      icon: '🎯',
      color: 'bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800',
      textColor: 'text-orange-600 dark:text-orange-400',
    },
  ]

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Budget Management
          </h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Manage your accounts, transactions, and budgets
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-5">
            <p className="text-sm text-gray-500 dark:text-gray-400">Total Balance</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
              {loading ? '...' : formatCurrency(stats.totalBalance)}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-5">
            <p className="text-sm text-gray-500 dark:text-gray-400">Accounts</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
              {loading ? '...' : stats.accountCount}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-5">
            <p className="text-sm text-gray-500 dark:text-gray-400">Transactions</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
              {loading ? '...' : stats.transactionCount}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-5">
            <p className="text-sm text-gray-500 dark:text-gray-400">Active Budgets</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
              {loading ? '...' : stats.budgetCount}
            </p>
          </div>
        </div>

        {/* Navigation Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {navigationCards.map((card) => (
            <Link
              key={card.href}
              href={card.href}
              className={`${card.color} border rounded-lg p-6 hover:shadow-md transition-all`}
            >
              <div className="flex items-start gap-4">
                <div className="text-4xl">{card.icon}</div>
                <div className="flex-1">
                  <h3 className={`text-lg font-semibold ${card.textColor} mb-1`}>
                    {card.title}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {card.description}
                  </p>
                </div>
                <svg
                  className={`w-5 h-5 ${card.textColor}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </div>
            </Link>
          ))}
        </div>

        {/* Budget Progress */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Budget Progress
            </h3>
            <Link
              href="/budget/budgets"
              className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
            >
              View all →
            </Link>
          </div>
          <BudgetProgress limit={3} />
        </div>
      </div>
    </AppLayout>
  )
}
