'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Sidebar from './Sidebar'
import Header from './Header'
import authService from '@/lib/auth'
import { User } from '@/types/auth'

interface AppLayoutProps {
  children: React.ReactNode
}

export default function AppLayout({ children }: AppLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const fetchUser = async () => {
      try {
        // Check if user is authenticated
        if (!authService.isAuthenticated()) {
          router.push('/auth/login')
          return
        }

        // Fetch current user
        const currentUser = await authService.getCurrentUser()
        setUser(currentUser)
      } catch (error) {
        console.error('Failed to fetch user:', error)
        // If fetch fails, redirect to login
        authService.logout()
      } finally {
        setIsLoading(false)
      }
    }

    fetchUser()
  }, [router])

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen)
  }

  const closeSidebar = () => {
    setIsSidebarOpen(false)
  }

  // Show loading spinner while fetching user
  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
          <p className="mt-2 text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    )
  }

  // Don't render layout if user is not loaded
  if (!user) {
    return null
  }

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <Sidebar isOpen={isSidebarOpen} onClose={closeSidebar} />

      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header onMenuClick={toggleSidebar} user={user} />

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
