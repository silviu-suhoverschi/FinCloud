'use client'

import { useState, useEffect, useRef } from 'react'
import { Asset } from '@/lib/portfolio'
import portfolioService from '@/lib/portfolio'

interface AssetSearchProps {
  onSelect: (asset: Asset) => void
  selectedAsset?: Asset | null
  className?: string
}

export default function AssetSearch({ onSelect, selectedAsset, className = '' }: AssetSearchProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Asset[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const searchRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowResults(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    if (selectedAsset) {
      setQuery(selectedAsset.symbol)
    }
  }, [selectedAsset])

  useEffect(() => {
    const searchAssets = async () => {
      if (query.length < 2) {
        setResults([])
        setShowResults(false)
        return
      }

      setIsSearching(true)
      try {
        const assets = await portfolioService.searchAssets(query)
        setResults(assets)
        setShowResults(true)
      } catch (err) {
        console.error('Asset search error:', err)
        setResults([])
      } finally {
        setIsSearching(false)
      }
    }

    const debounceTimer = setTimeout(searchAssets, 300)
    return () => clearTimeout(debounceTimer)
  }, [query])

  const handleSelect = (asset: Asset) => {
    setQuery(asset.symbol)
    setShowResults(false)
    onSelect(asset)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value)
    if (selectedAsset && e.target.value !== selectedAsset.symbol) {
      // Clear selection if query changes
      onSelect(null as any)
    }
  }

  return (
    <div ref={searchRef} className={`relative ${className}`}>
      <input
        type="text"
        value={query}
        onChange={handleInputChange}
        onFocus={() => {
          if (results.length > 0) setShowResults(true)
        }}
        placeholder="Search for stocks, ETFs, crypto..."
        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
      />

      {isSearching && (
        <div className="absolute right-3 top-3">
          <div className="animate-spin h-4 w-4 border-2 border-blue-500 rounded-full border-t-transparent"></div>
        </div>
      )}

      {showResults && results.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {results.map((asset) => (
            <button
              key={asset.id}
              onClick={() => handleSelect(asset)}
              className="w-full px-4 py-3 text-left hover:bg-gray-100 dark:hover:bg-gray-700 border-b border-gray-200 dark:border-gray-700 last:border-b-0"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="font-medium text-gray-900 dark:text-white">{asset.symbol}</div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">{asset.name}</div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 capitalize">
                    {asset.type}
                  </span>
                  {asset.exchange && (
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {asset.exchange}
                    </span>
                  )}
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      {showResults && results.length === 0 && query.length >= 2 && !isSearching && (
        <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg p-4 text-center">
          <p className="text-sm text-gray-500 dark:text-gray-400">No assets found</p>
        </div>
      )}
    </div>
  )
}
