'use client'

import { useState, useEffect, useCallback } from 'react'
import { useParams, useRouter } from 'next/navigation'
import AppLayout from '@/components/layout/AppLayout'
import budgetService, { Budget, Category, UpdateBudgetData } from '@/lib/budget'
import Link from 'next/link'

export default function EditBudgetPage() {
  const params = useParams()
  const router = useRouter()
  const budgetId = parseInt(params.id as string)

  const [budget, setBudget] = useState<Budget | null>(null)
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  const [formData, setFormData] = useState<UpdateBudgetData>({})
  const [errors, setErrors] = useState<Record<string, string>>({})

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      const [budgetData, categoriesData] = await Promise.all([
        budgetService.getBudget(budgetId),
        budgetService.getCategories(),
      ])

      // Only show expense categories for budgets
      const expenseCategories = categoriesData.filter((cat) => cat.type === 'expense')

      setBudget(budgetData)
      setCategories(expenseCategories)

      setFormData({
        category_id: budgetData.category_id,
        amount: budgetData.amount,
        period: budgetData.period,
        start_date: budgetData.start_date.split('T')[0],
        end_date: budgetData.end_date ? budgetData.end_date.split('T')[0] : undefined,
      })
    } catch (err) {
      alert('Failed to load budget')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }, [budgetId])

  useEffect(() => {
    loadData()
  }, [loadData])

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.category_id) {
      newErrors.category_id = 'Please select a category'
    }
    if (!formData.amount || formData.amount <= 0) {
      newErrors.amount = 'Amount must be greater than 0'
    }
    if (!formData.start_date) {
      newErrors.start_date = 'Start date is required'
    }
    if (formData.end_date && formData.start_date && formData.end_date < formData.start_date) {
      newErrors.end_date = 'End date must be after start date'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    try {
      setSubmitting(true)
      await budgetService.updateBudget(budgetId, formData)
      router.push('/budget/budgets')
    } catch (err) {
      alert('Failed to update budget')
      console.error(err)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this budget?')) return

    try {
      await budgetService.deleteBudget(budgetId)
      router.push('/budget/budgets')
    } catch (err) {
      alert('Failed to delete budget')
      console.error(err)
    }
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
          <p className="text-gray-500 dark:text-gray-400">Loading...</p>
        </div>
      </AppLayout>
    )
  }

  if (!budget) {
    return (
      <AppLayout>
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-800 dark:text-red-200">Budget not found</p>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <Link
              href="/budget/budgets"
              className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 mb-4 inline-block"
            >
              ← Back to Budgets
            </Link>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Edit Budget
            </h2>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Update budget details
            </p>
          </div>
          <button
            onClick={handleDelete}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Delete
          </button>
        </div>

        {/* Form */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Category */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Category <span className="text-red-500">*</span>
              </label>
              <select
                required
                value={formData.category_id || budget.category_id}
                onChange={(e) => setFormData({ ...formData, category_id: parseInt(e.target.value) })}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white ${
                  errors.category_id ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                }`}
              >
                <option value="">Select a category</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
              {errors.category_id && (
                <p className="mt-1 text-sm text-red-500">{errors.category_id}</p>
              )}
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Only expense categories can have budgets
              </p>
            </div>

            {/* Amount */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Budget Amount <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                required
                step="0.01"
                min="0.01"
                value={formData.amount ?? budget.amount}
                onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) })}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white ${
                  errors.amount ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                }`}
                placeholder="0.00"
              />
              {errors.amount && (
                <p className="mt-1 text-sm text-red-500">{errors.amount}</p>
              )}
            </div>

            {/* Period */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Budget Period <span className="text-red-500">*</span>
              </label>
              <div className="flex gap-4">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    value="monthly"
                    checked={(formData.period || budget.period) === 'monthly'}
                    onChange={(e) => setFormData({ ...formData, period: e.target.value as any })}
                    className="mr-2"
                  />
                  <span className="text-gray-700 dark:text-gray-300">Monthly</span>
                </label>
                <label className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    value="yearly"
                    checked={(formData.period || budget.period) === 'yearly'}
                    onChange={(e) => setFormData({ ...formData, period: e.target.value as any })}
                    className="mr-2"
                  />
                  <span className="text-gray-700 dark:text-gray-300">Yearly</span>
                </label>
              </div>
            </div>

            {/* Start Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Start Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                required
                value={formData.start_date ?? budget.start_date.split('T')[0]}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white ${
                  errors.start_date ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                }`}
              />
              {errors.start_date && (
                <p className="mt-1 text-sm text-red-500">{errors.start_date}</p>
              )}
            </div>

            {/* End Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                End Date (Optional)
              </label>
              <input
                type="date"
                value={formData.end_date ?? (budget.end_date ? budget.end_date.split('T')[0] : '')}
                onChange={(e) => setFormData({ ...formData, end_date: e.target.value || undefined })}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white ${
                  errors.end_date ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                }`}
              />
              {errors.end_date && (
                <p className="mt-1 text-sm text-red-500">{errors.end_date}</p>
              )}
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Leave empty for ongoing budget
              </p>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <Link
                href="/budget/budgets"
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-center"
              >
                Cancel
              </Link>
              <button
                type="submit"
                disabled={submitting}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {submitting ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </AppLayout>
  )
}
