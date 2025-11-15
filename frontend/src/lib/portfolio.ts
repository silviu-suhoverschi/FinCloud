import api from './api'

export interface Portfolio {
  id: number
  user_id: number
  name: string
  description?: string
  created_at: string
  updated_at: string
}

export interface Asset {
  id: number
  symbol: string
  name: string
  type: 'stock' | 'etf' | 'crypto' | 'bond' | 'commodity' | 'currency' | 'other'
  exchange?: string
  current_price?: number
  currency?: string
}

export interface Holding {
  id: number
  portfolio_id: number
  asset_id: number
  quantity: number
  average_buy_price: number
  current_price?: number
  current_value?: number
  gain_loss?: number
  gain_loss_percentage?: number
  asset?: Asset
}

export interface PortfolioTransaction {
  id: number
  portfolio_id: number
  asset_id: number
  transaction_type: 'BUY' | 'SELL' | 'DIVIDEND' | 'SPLIT' | 'INTEREST' | 'FEE' | 'TAX' | 'TRANSFER_IN' | 'TRANSFER_OUT'
  quantity: number
  price: number
  fee?: number
  tax?: number
  date: string
  notes?: string
  created_at: string
  updated_at: string
  asset?: Asset
}

export interface PortfolioPerformance {
  total_value: number
  total_cost: number
  total_gain_loss: number
  total_gain_loss_percentage: number
  roi: number
  xirr?: number
  twr?: number
  asset_allocation: {
    asset_type: string
    value: number
    percentage: number
  }[]
}

export interface PortfolioValueHistory {
  date: string
  value: number
}

export interface CreatePortfolioData {
  name: string
  description?: string
}

export interface UpdatePortfolioData {
  name?: string
  description?: string
}

export interface CreateHoldingData {
  portfolio_id: number
  asset_id: number
  quantity: number
  average_buy_price: number
}

export interface UpdateHoldingData {
  quantity?: number
  average_buy_price?: number
}

export interface CreateTransactionData {
  portfolio_id: number
  asset_id: number
  transaction_type: 'BUY' | 'SELL' | 'DIVIDEND' | 'SPLIT' | 'INTEREST' | 'FEE' | 'TAX' | 'TRANSFER_IN' | 'TRANSFER_OUT'
  quantity: number
  price: number
  fee?: number
  tax?: number
  date: string
  notes?: string
}

export interface UpdateTransactionData {
  transaction_type?: 'BUY' | 'SELL' | 'DIVIDEND' | 'SPLIT' | 'INTEREST' | 'FEE' | 'TAX' | 'TRANSFER_IN' | 'TRANSFER_OUT'
  quantity?: number
  price?: number
  fee?: number
  tax?: number
  date?: string
  notes?: string
}

export const portfolioService = {
  // Portfolios
  async getPortfolios(): Promise<Portfolio[]> {
    const response = await api.get<Portfolio[]>('/api/v1/portfolios')
    return response.data
  },

  async getPortfolio(id: number): Promise<Portfolio> {
    const response = await api.get<Portfolio>(`/api/v1/portfolios/${id}`)
    return response.data
  },

  async createPortfolio(data: CreatePortfolioData): Promise<Portfolio> {
    const response = await api.post<Portfolio>('/api/v1/portfolios', data)
    return response.data
  },

  async updatePortfolio(id: number, data: UpdatePortfolioData): Promise<Portfolio> {
    const response = await api.put<Portfolio>(`/api/v1/portfolios/${id}`, data)
    return response.data
  },

  async deletePortfolio(id: number): Promise<void> {
    await api.delete(`/api/v1/portfolios/${id}`)
  },

  // Assets
  async searchAssets(query: string, type?: string): Promise<Asset[]> {
    const params = type ? { q: query, type } : { q: query }
    const response = await api.get<Asset[]>('/api/v1/assets/search', { params })
    return response.data
  },

  async getAsset(id: number): Promise<Asset> {
    const response = await api.get<Asset>(`/api/v1/assets/${id}`)
    return response.data
  },

  // Holdings
  async getHoldings(portfolioId?: number): Promise<Holding[]> {
    const params = portfolioId ? { portfolio_id: portfolioId } : {}
    const response = await api.get<Holding[]>('/api/v1/holdings', { params })
    return response.data
  },

  async getHolding(id: number): Promise<Holding> {
    const response = await api.get<Holding>(`/api/v1/holdings/${id}`)
    return response.data
  },

  async createHolding(data: CreateHoldingData): Promise<Holding> {
    const response = await api.post<Holding>('/api/v1/holdings', data)
    return response.data
  },

  async updateHolding(id: number, data: UpdateHoldingData): Promise<Holding> {
    const response = await api.put<Holding>(`/api/v1/holdings/${id}`, data)
    return response.data
  },

  async deleteHolding(id: number): Promise<void> {
    await api.delete(`/api/v1/holdings/${id}`)
  },

  // Transactions
  async getTransactions(portfolioId?: number): Promise<PortfolioTransaction[]> {
    const params = portfolioId ? { portfolio_id: portfolioId } : {}
    const response = await api.get<PortfolioTransaction[]>('/api/v1/transactions', { params })
    return response.data
  },

  async getTransaction(id: number): Promise<PortfolioTransaction> {
    const response = await api.get<PortfolioTransaction>(`/api/v1/transactions/${id}`)
    return response.data
  },

  async createTransaction(data: CreateTransactionData): Promise<PortfolioTransaction> {
    const response = await api.post<PortfolioTransaction>('/api/v1/transactions', data)
    return response.data
  },

  async updateTransaction(id: number, data: UpdateTransactionData): Promise<PortfolioTransaction> {
    const response = await api.put<PortfolioTransaction>(`/api/v1/transactions/${id}`, data)
    return response.data
  },

  async deleteTransaction(id: number): Promise<void> {
    await api.delete(`/api/v1/transactions/${id}`)
  },

  // Performance & Analytics
  async getPortfolioPerformance(portfolioId: number): Promise<PortfolioPerformance> {
    const response = await api.get<PortfolioPerformance>(
      `/api/v1/portfolios/${portfolioId}/performance`
    )
    return response.data
  },

  async getTotalPortfolioValue(): Promise<number> {
    const portfolios = await this.getPortfolios()
    let totalValue = 0

    for (const portfolio of portfolios) {
      try {
        const performance = await this.getPortfolioPerformance(portfolio.id)
        totalValue += performance.total_value
      } catch (error) {
        console.error(`Error fetching performance for portfolio ${portfolio.id}:`, error)
      }
    }

    return totalValue
  },

  async getPortfolioValueHistory(
    portfolioId: number,
    days: number = 30
  ): Promise<PortfolioValueHistory[]> {
    const response = await api.get<PortfolioValueHistory[]>(
      `/api/v1/portfolios/${portfolioId}/history`,
      {
        params: { days },
      }
    )
    return response.data
  },
}

export default portfolioService
