import api from './api'

export interface Account {
  id: number
  user_id: number
  name: string
  type: 'checking' | 'savings' | 'cash' | 'credit_card' | 'investment' | 'loan' | 'mortgage' | 'other'
  currency: string
  current_balance: number
  initial_balance?: number
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

export interface CreateAccountData {
  name: string
  type: 'checking' | 'savings' | 'cash' | 'credit_card' | 'investment' | 'loan' | 'mortgage' | 'other'
  currency: string
  initial_balance: number
}

export interface UpdateAccountData {
  name?: string
  type?: 'checking' | 'savings' | 'cash' | 'credit_card' | 'investment' | 'loan' | 'mortgage' | 'other'
  currency?: string
  current_balance?: number
}

export interface CreateTransactionData {
  account_id: number
  category_id?: number
  amount: number
  currency: string
  description: string
  date: string
  type: 'income' | 'expense'
}

export interface UpdateTransactionData {
  account_id?: number
  category_id?: number
  amount?: number
  description?: string
  date?: string
  type?: 'income' | 'expense'
}

export interface CreateCategoryData {
  name: string
  type: 'income' | 'expense'
  parent_id?: number
}

export interface UpdateCategoryData {
  name?: string
  type?: 'income' | 'expense'
  parent_id?: number
}

export interface CreateBudgetData {
  category_id: number
  amount: number
  period: 'monthly' | 'yearly'
  start_date: string
  end_date?: string
}

export interface UpdateBudgetData {
  category_id?: number
  amount?: number
  period?: 'monthly' | 'yearly'
  start_date?: string
  end_date?: string
}

export const budgetService = {
  // Accounts
  async getAccounts(): Promise<Account[]> {
    const response = await api.get<{ total: number; accounts: Account[] }>('/api/v1/accounts')
    return response.data.accounts || []
  },

  async getAccount(id: number): Promise<Account> {
    const response = await api.get<Account>(`/api/v1/accounts/${id}`)
    return response.data
  },

  async createAccount(data: CreateAccountData): Promise<Account> {
    const response = await api.post<Account>('/api/v1/accounts', data)
    return response.data
  },

  async updateAccount(id: number, data: UpdateAccountData): Promise<Account> {
    const response = await api.put<Account>(`/api/v1/accounts/${id}`, data)
    return response.data
  },

  async deleteAccount(id: number): Promise<void> {
    await api.delete(`/api/v1/accounts/${id}`)
  },

  async getTotalBalance(): Promise<number> {
    const accounts = await this.getAccounts()
    return accounts.reduce((sum, account) => sum + account.current_balance, 0)
  },

  async getAccountBalance(id: number): Promise<{ balance: number }> {
    const response = await api.get<{ balance: number }>(`/api/v1/accounts/${id}/balance`)
    return response.data
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
    const response = await api.get<{ total: number; transactions: Transaction[] }>('/api/v1/transactions', { params })
    return response.data.transactions || []
  },

  async getTransaction(id: number): Promise<Transaction> {
    const response = await api.get<Transaction>(`/api/v1/transactions/${id}`)
    return response.data
  },

  async createTransaction(data: CreateTransactionData): Promise<Transaction> {
    const response = await api.post<Transaction>('/api/v1/transactions', data)
    return response.data
  },

  async updateTransaction(id: number, data: UpdateTransactionData): Promise<Transaction> {
    const response = await api.put<Transaction>(`/api/v1/transactions/${id}`, data)
    return response.data
  },

  async deleteTransaction(id: number): Promise<void> {
    await api.delete(`/api/v1/transactions/${id}`)
  },

  async getRecentTransactions(limit: number = 5): Promise<Transaction[]> {
    return this.getTransactions({ limit })
  },

  // Categories
  async getCategories(): Promise<Category[]> {
    const response = await api.get<{ total: number; categories: Category[] }>('/api/v1/categories')
    return response.data.categories || []
  },

  async getCategory(id: number): Promise<Category> {
    const response = await api.get<Category>(`/api/v1/categories/${id}`)
    return response.data
  },

  async createCategory(data: CreateCategoryData): Promise<Category> {
    const response = await api.post<Category>('/api/v1/categories', data)
    return response.data
  },

  async updateCategory(id: number, data: UpdateCategoryData): Promise<Category> {
    const response = await api.put<Category>(`/api/v1/categories/${id}`, data)
    return response.data
  },

  async deleteCategory(id: number): Promise<void> {
    await api.delete(`/api/v1/categories/${id}`)
  },

  async getCategoryTree(): Promise<Category[]> {
    const response = await api.get<{ categories: Category[] }>('/api/v1/categories/tree')
    return response.data.categories || []
  },

  // Budgets
  async getBudgets(): Promise<Budget[]> {
    try {
      const response = await api.get<Budget[]>('/api/v1/budgets')
      return Array.isArray(response.data) ? response.data : []
    } catch (error) {
      console.error('Error fetching budgets:', error)
      return []
    }
  },

  async getBudget(id: number): Promise<Budget> {
    const response = await api.get<Budget>(`/api/v1/budgets/${id}`)
    return response.data
  },

  async createBudget(data: CreateBudgetData): Promise<Budget> {
    const response = await api.post<Budget>('/api/v1/budgets', data)
    return response.data
  },

  async updateBudget(id: number, data: UpdateBudgetData): Promise<Budget> {
    const response = await api.put<Budget>(`/api/v1/budgets/${id}`, data)
    return response.data
  },

  async deleteBudget(id: number): Promise<void> {
    await api.delete(`/api/v1/budgets/${id}`)
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
}

export default budgetService
