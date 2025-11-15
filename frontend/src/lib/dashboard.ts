import budgetService from './budget'
import portfolioService from './portfolio'
import reportsService from './reports'

export interface DashboardMetrics {
  totalBalance: number
  portfolioValue: number
  monthlySpending: number
  netWorth: number
  balanceChange?: number
  portfolioROI?: number
  budgetUsage?: number
  netWorthChange?: number
}

export const dashboardService = {
  async getMetrics(): Promise<DashboardMetrics> {
    try {
      // Fetch all data in parallel
      const [totalBalance, portfolioValue, portfolios, budgets, netWorthData] = await Promise.all([
        budgetService.getTotalBalance().catch(() => 0),
        portfolioService.getTotalPortfolioValue().catch(() => 0),
        portfolioService.getPortfolios().catch(() => []),
        budgetService.getBudgets().catch(() => []),
        reportsService
          .getNetWorth({
            interval: 'monthly',
          })
          .catch(() => []),
      ])

      // Calculate monthly spending from recent transactions
      const now = new Date()
      const firstDayOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
      const monthlyTransactions = await budgetService
        .getTransactions({
          start_date: firstDayOfMonth.toISOString().split('T')[0],
          type: 'expense',
        })
        .catch(() => [])

      const monthlySpending = monthlyTransactions.reduce(
        (sum, transaction) => sum + Math.abs(transaction.amount),
        0
      )

      // Calculate net worth
      const netWorth = totalBalance + portfolioValue

      // Calculate portfolio ROI
      let portfolioROI = 0
      if (portfolios.length > 0) {
        try {
          const performance = await portfolioService.getPortfolioPerformance(portfolios[0].id)
          portfolioROI = performance.roi || 0
        } catch (error) {
          console.error('Error fetching portfolio performance:', error)
        }
      }

      // Calculate budget usage
      let budgetUsage = 0
      if (budgets.length > 0) {
        const totalBudget = budgets.reduce((sum, budget) => sum + budget.amount, 0)
        if (totalBudget > 0) {
          budgetUsage = (monthlySpending / totalBudget) * 100
        }
      }

      // Calculate net worth change (YTD)
      let netWorthChange = 0
      if (netWorthData.length >= 2) {
        const oldestValue = netWorthData[0].net_worth
        const latestValue = netWorthData[netWorthData.length - 1].net_worth
        if (oldestValue > 0) {
          netWorthChange = ((latestValue - oldestValue) / oldestValue) * 100
        }
      }

      return {
        totalBalance,
        portfolioValue,
        monthlySpending,
        netWorth,
        portfolioROI,
        budgetUsage,
        netWorthChange,
      }
    } catch (error) {
      console.error('Error fetching dashboard metrics:', error)
      return {
        totalBalance: 0,
        portfolioValue: 0,
        monthlySpending: 0,
        netWorth: 0,
      }
    }
  },
}

export default dashboardService
