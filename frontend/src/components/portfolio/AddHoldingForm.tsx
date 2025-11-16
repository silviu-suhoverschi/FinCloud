'use client'

import { useState } from 'react'
import { Asset } from '@/lib/portfolio'
import portfolioService from '@/lib/portfolio'
import AssetSearch from './AssetSearch'

interface AddHoldingFormProps {
  portfolioId: number
  onSuccess: () => void
  onCancel: () => void
}

export default function AddHoldingForm({ portfolioId, onSuccess, onCancel }: AddHoldingFormProps) {
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null)
  const [formData, setFormData] = useState({
    quantity: '',
    average_cost: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!selectedAsset) {
      setError('Please select an asset')
      return
    }

    if (!formData.quantity || !formData.average_cost) {
      setError('Please fill in all required fields')
      return
    }

    try {
      setSubmitting(true)
      setError(null)

      await portfolioService.createHolding({
        portfolio_id: portfolioId,
        asset_id: selectedAsset.id,
        quantity: parseFloat(formData.quantity),
        average_cost: parseFloat(formData.average_cost),
      })

      onSuccess()
    } catch (err: any) {
      // Handle different error response formats
      let errorMessage = 'Failed to add holding'

      if (err.response?.data?.detail) {
        const detail = err.response.data.detail
        // Check if detail is an array (validation errors)
        if (Array.isArray(detail)) {
          // Extract error messages from validation errors
          errorMessage = detail.map((e: any) => e.msg || e.message || 'Validation error').join(', ')
        } else if (typeof detail === 'string') {
          // Detail is a string
          errorMessage = detail
        }
      }

      setError(errorMessage)
      console.error(err)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
          <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Asset *
        </label>
        <AssetSearch
          onSelect={setSelectedAsset}
          selectedAsset={selectedAsset}
        />
        {selectedAsset && (
          <div className="mt-2 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-blue-900 dark:text-blue-100">
                  {selectedAsset.symbol}
                </div>
                <div className="text-sm text-blue-700 dark:text-blue-300">
                  {selectedAsset.name}
                </div>
              </div>
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-200 capitalize">
                {selectedAsset.type}
              </span>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Quantity *
          </label>
          <input
            type="number"
            value={formData.quantity}
            onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder="10"
            step="0.00000001"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Average Cost *
          </label>
          <input
            type="number"
            value={formData.average_cost}
            onChange={(e) => setFormData({ ...formData, average_cost: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder="100.00"
            step="0.01"
            required
          />
        </div>
      </div>

      {selectedAsset && formData.quantity && formData.average_cost && (
        <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">Total Investment:</span>
            <span className="text-lg font-semibold text-gray-900 dark:text-white">
              {new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
              }).format(parseFloat(formData.quantity) * parseFloat(formData.average_cost))}
            </span>
          </div>
        </div>
      )}

      <div className="flex gap-2 justify-end pt-4">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={submitting || !selectedAsset}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {submitting ? 'Adding...' : 'Add Holding'}
        </button>
      </div>
    </form>
  )
}
