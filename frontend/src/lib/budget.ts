import api from './api'

export interface Account {
  id: number
  user_id: number
  name: string
  type: 'bank' | 'savings' | 'cash' | 'credit' | 'investment'
  currency: string
  balance: number
  created_at: string
  updated_at: string
}

export interface Transaction {
  id: number
  account_id: number
  category_id?: number
  amount: number
  description: string
  date: string
  type: 'income' | 'expense'
  created_at: string
  updated_at: string
  category?: {
    id: number
    name: string
    type: string
  }
  account?: {
    id: number
    name: string
  }
}

export interface Budget {
  id: number
  user_id: number
  category_id: number
  amount: number
  period: 'monthly' | 'yearly'
  start_date: string
  end_date?: string
  spent?: number
  remaining?: number
  category?: {
    id: number
    name: string
    type: string
  }
}

export interface Category {
  id: number
  user_id: number
  name: string
  type: 'income' | 'expense'
  parent_id?: number
  created_at: string
  updated_at: string
}

export const budgetService = {
  // Accounts
  async getAccounts(): Promise<Account[]> {
    const response = await api.get<Account[]>('/api/v1/accounts')
    return response.data
  },

  async getAccount(id: number): Promise<Account> {
    const response = await api.get<Account>(`/api/v1/accounts/${id}`)
    return response.data
  },

  async getTotalBalance(): Promise<number> {
    const accounts = await this.getAccounts()
    return accounts.reduce((sum, account) => sum + account.balance, 0)
  },

  // Transactions
  async getTransactions(params?: {
    limit?: number
    offset?: number
    account_id?: number
    category_id?: number
    type?: string
    start_date?: string
    end_date?: string
  }): Promise<Transaction[]> {
    const response = await api.get<Transaction[]>('/api/v1/transactions', { params })
    return response.data
  },

  async getRecentTransactions(limit: number = 5): Promise<Transaction[]> {
    return this.getTransactions({ limit })
  },

  // Budgets
  async getBudgets(): Promise<Budget[]> {
    const response = await api.get<Budget[]>('/api/v1/budgets')
    return response.data
  },

  async getBudgetProgress(id: number): Promise<{
    budget: Budget
    spent: number
    remaining: number
    percentage: number
  }> {
    const response = await api.get(`/api/v1/budgets/${id}/progress`)
    return response.data
  },

  // Categories
  async getCategories(): Promise<Category[]> {
    const response = await api.get<Category[]>('/api/v1/categories')
    return response.data
  },
}

export default budgetService
