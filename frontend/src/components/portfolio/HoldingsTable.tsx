'use client'

import { useState } from 'react'
import { Holding } from '@/lib/portfolio'
import portfolioService from '@/lib/portfolio'

interface HoldingsTableProps {
  holdings: Holding[]
  onUpdate: () => void
}

export default function HoldingsTable({ holdings, onUpdate }: HoldingsTableProps) {
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editForm, setEditForm] = useState({ quantity: 0, average_cost: 0 })

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount)
  }

  const formatPercentage = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
  }

  const handleEdit = (holding: Holding) => {
    setEditingId(holding.id)
    setEditForm({
      quantity: holding.quantity,
      average_cost: holding.average_cost,
    })
  }

  const handleSave = async (id: number) => {
    try {
      await portfolioService.updateHolding(id, editForm)
      setEditingId(null)
      onUpdate()
    } catch (err) {
      alert('Failed to update holding')
      console.error(err)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this holding?')) return

    try {
      await portfolioService.deleteHolding(id)
      onUpdate()
    } catch (err) {
      alert('Failed to delete holding')
      console.error(err)
    }
  }

  if (holdings.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center border border-gray-200 dark:border-gray-700">
        <p className="text-gray-500 dark:text-gray-400">No holdings yet. Add your first holding!</p>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 dark:bg-gray-700">
            <tr>
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
                Avg Buy Price
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Current Price
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Current Value
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Gain/Loss
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {holdings.map((holding) => (
              <tr key={holding.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                <td className="px-4 py-3">
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">
                      {holding.asset?.symbol || 'N/A'}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {holding.asset?.name || 'Unknown'}
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 capitalize">
                    {holding.asset?.type || 'N/A'}
                  </span>
                </td>
                <td className="px-4 py-3 text-right">
                  {editingId === holding.id ? (
                    <input
                      type="number"
                      value={editForm.quantity}
                      onChange={(e) =>
                        setEditForm({ ...editForm, quantity: parseFloat(e.target.value) })
                      }
                      className="w-24 px-2 py-1 text-right border border-gray-300 dark:border-gray-600 rounded dark:bg-gray-700 dark:text-white"
                      step="0.00000001"
                    />
                  ) : (
                    <span className="text-gray-900 dark:text-white">
                      {holding.quantity.toLocaleString()}
                    </span>
                  )}
                </td>
                <td className="px-4 py-3 text-right">
                  {editingId === holding.id ? (
                    <input
                      type="number"
                      value={editForm.average_cost}
                      onChange={(e) =>
                        setEditForm({
                          ...editForm,
                          average_cost: parseFloat(e.target.value),
                        })
                      }
                      className="w-24 px-2 py-1 text-right border border-gray-300 dark:border-gray-600 rounded dark:bg-gray-700 dark:text-white"
                      step="0.01"
                    />
                  ) : (
                    <span className="text-gray-900 dark:text-white">
                      {formatCurrency(holding.average_cost)}
                    </span>
                  )}
                </td>
                <td className="px-4 py-3 text-right text-gray-900 dark:text-white">
                  {holding.current_price ? formatCurrency(holding.current_price) : 'N/A'}
                </td>
                <td className="px-4 py-3 text-right text-gray-900 dark:text-white">
                  {holding.current_value ? formatCurrency(holding.current_value) : 'N/A'}
                </td>
                <td className="px-4 py-3 text-right">
                  {holding.unrealized_gain_loss !== undefined && holding.unrealized_gain_loss_percent !== undefined ? (
                    <div>
                      <div
                        className={`font-medium ${
                          holding.unrealized_gain_loss >= 0
                            ? 'text-green-600 dark:text-green-400'
                            : 'text-red-600 dark:text-red-400'
                        }`}
                      >
                        {formatCurrency(holding.unrealized_gain_loss)}
                      </div>
                      <div
                        className={`text-sm ${
                          holding.unrealized_gain_loss_percent >= 0
                            ? 'text-green-600 dark:text-green-400'
                            : 'text-red-600 dark:text-red-400'
                        }`}
                      >
                        {formatPercentage(holding.unrealized_gain_loss_percent)}
                      </div>
                    </div>
                  ) : (
                    <span className="text-gray-500">N/A</span>
                  )}
                </td>
                <td className="px-4 py-3 text-right">
                  {editingId === holding.id ? (
                    <div className="flex gap-1 justify-end">
                      <button
                        onClick={() => handleSave(holding.id)}
                        className="text-green-600 dark:text-green-400 hover:underline text-sm"
                      >
                        Save
                      </button>
                      <button
                        onClick={() => setEditingId(null)}
                        className="text-gray-600 dark:text-gray-400 hover:underline text-sm"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <div className="flex gap-1 justify-end">
                      <button
                        onClick={() => handleEdit(holding)}
                        className="text-blue-600 dark:text-blue-400 hover:underline text-sm"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(holding.id)}
                        className="text-red-600 dark:text-red-400 hover:underline text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
