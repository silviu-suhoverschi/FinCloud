import api from './api'

export interface NetWorthDataPoint {
  date: string
  assets: number
  liabilities: number
  net_worth: number
}

export interface CashflowDataPoint {
  date: string
  income: number
  expenses: number
  net: number
}

export interface SpendingByCategory {
  category: string
  amount: number
  percentage: number
}

export interface IncomeByCategory {
  category: string
  amount: number
  percentage: number
}

export const reportsService = {
  // Net Worth Timeline
  async getNetWorth(params?: {
    start_date?: string
    end_date?: string
    interval?: 'daily' | 'weekly' | 'monthly'
  }): Promise<NetWorthDataPoint[]> {
    const response = await api.get<NetWorthDataPoint[]>('/api/v1/reports/net-worth', { params })
    return response.data
  },

  // Cashflow
  async getCashflow(params?: {
    start_date?: string
    end_date?: string
    interval?: 'daily' | 'weekly' | 'monthly'
  }): Promise<CashflowDataPoint[]> {
    const response = await api.get<CashflowDataPoint[]>('/api/v1/reports/cashflow', { params })
    return response.data
  },

  // Spending by Category
  async getSpending(params?: {
    start_date?: string
    end_date?: string
  }): Promise<SpendingByCategory[]> {
    const response = await api.get<SpendingByCategory[]>('/api/v1/reports/spending', { params })
    return response.data
  },

  // Income Analysis
  async getIncome(params?: {
    start_date?: string
    end_date?: string
  }): Promise<IncomeByCategory[]> {
    const response = await api.get<IncomeByCategory[]>('/api/v1/reports/income', { params })
    return response.data
  },
}

export default reportsService
