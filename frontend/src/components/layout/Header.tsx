'use client'

import { MenuIcon, SunIcon, MoonIcon } from '@/components/icons'
import { useTheme } from '@/providers/ThemeProvider'
import UserDropdown from './UserDropdown'
import { User } from '@/types/auth'

interface HeaderProps {
  onMenuClick: () => void
  user: User
}

export default function Header({ onMenuClick, user }: HeaderProps) {
  const { theme, toggleTheme } = useTheme()

  return (
    <header className="sticky top-0 z-10 flex items-center justify-between h-16 px-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      {/* Left side - Mobile menu button */}
      <div className="flex items-center">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          <MenuIcon className="h-6 w-6" />
        </button>
        <div className="ml-4 lg:ml-0">
          <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
            Dashboard
          </h1>
        </div>
      </div>

      {/* Right side - Theme toggle and user dropdown */}
      <div className="flex items-center space-x-4">
        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? (
            <SunIcon className="w-5 h-5 text-gray-500 dark:text-gray-400" />
          ) : (
            <MoonIcon className="w-5 h-5 text-gray-500 dark:text-gray-400" />
          )}
        </button>

        {/* User dropdown */}
        <UserDropdown user={user} />
      </div>
    </header>
  )
}
