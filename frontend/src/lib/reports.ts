import api from './api'

// Types matching backend schema
export interface CashflowDataPoint {
  month: string
  income: number
  expenses: number
  net: number
  currency: string
}

export interface CashflowReport {
  start_date: string
  end_date: string
  currency: string
  data: CashflowDataPoint[]
  total_income: number
  total_expenses: number
  net_cashflow: number
}

export interface CategorySpending {
  category_id: number | null
  category_name: string
  total_amount: number
  transaction_count: number
  percentage: number
}

export interface SpendingReport {
  start_date: string
  end_date: string
  currency: string
  categories: CategorySpending[]
  total_spending: number
  total_transactions: number
}

export interface IncomeSource {
  category_id: number | null
  category_name: string
  total_amount: number
  transaction_count: number
  percentage: number
}

export interface IncomeReport {
  start_date: string
  end_date: string
  currency: string
  sources: IncomeSource[]
  total_income: number
  total_transactions: number
  average_monthly_income: number
}

export interface NetWorthDataPoint {
  date: string
  total_assets: number
  total_liabilities: number
  net_worth: number
  currency: string
}

export interface AccountBalance {
  account_id: number
  account_name: string
  account_type: string
  balance: number
  currency: string
}

export interface NetWorthReport {
  start_date: string
  end_date: string
  currency: string
  timeline: NetWorthDataPoint[]
  current_net_worth: number
  change: number
  change_percentage: number
  accounts: AccountBalance[]
}

// Legacy types for backward compatibility
export interface NetWorthDataPointLegacy {
  date: string
  assets: number
  liabilities: number
  net_worth: number
}

export const reportsService = {
  // Net Worth Timeline
  async getNetWorth(params: {
    start_date: string
    end_date: string
    currency?: string
  }): Promise<NetWorthReport> {
    const response = await api.get<NetWorthReport>('/api/v1/reports/net-worth', { params })
    return response.data
  },

  // Legacy method for backward compatibility
  async getNetWorthLegacy(params?: {
    start_date?: string
    end_date?: string
    interval?: 'daily' | 'weekly' | 'monthly'
  }): Promise<NetWorthDataPointLegacy[]> {
    const endDate = params?.end_date || new Date().toISOString().split('T')[0]
    const startDate = params?.start_date || new Date(new Date().setMonth(new Date().getMonth() - 6)).toISOString().split('T')[0]

    const response = await api.get<NetWorthReport>('/api/v1/reports/net-worth', {
      params: { start_date: startDate, end_date: endDate }
    })

    // Convert to legacy format
    return response.data.timeline.map(point => ({
      date: point.date,
      assets: point.total_assets,
      liabilities: point.total_liabilities,
      net_worth: point.net_worth
    }))
  },

  // Cashflow
  async getCashflow(params: {
    start_date: string
    end_date: string
    currency?: string
  }): Promise<CashflowReport> {
    const response = await api.get<CashflowReport>('/api/v1/reports/cashflow', { params })
    return response.data
  },

  // Spending by Category
  async getSpending(params: {
    start_date: string
    end_date: string
    currency?: string
  }): Promise<SpendingReport> {
    const response = await api.get<SpendingReport>('/api/v1/reports/spending', { params })
    return response.data
  },

  // Income Analysis
  async getIncome(params: {
    start_date: string
    end_date: string
    currency?: string
  }): Promise<IncomeReport> {
    const response = await api.get<IncomeReport>('/api/v1/reports/income', { params })
    return response.data
  },
}

export default reportsService
