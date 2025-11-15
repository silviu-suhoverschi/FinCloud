import api from './api'

export interface Portfolio {
  id: number
  user_id: number
  name: string
  description?: string
  created_at: string
  updated_at: string
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
  asset?: {
    id: number
    symbol: string
    name: string
    type: string
    exchange?: string
  }
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

  // Holdings
  async getHoldings(portfolioId?: number): Promise<Holding[]> {
    const params = portfolioId ? { portfolio_id: portfolioId } : {}
    const response = await api.get<Holding[]>('/api/v1/holdings', { params })
    return response.data
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
