'use client'

import { useState, useEffect } from 'react'
import AppLayout from '@/components/layout/AppLayout'
import {
  getUserProfile,
  updateUserProfile,
  changePassword,
  getApiKeys,
  createApiKey,
  deleteApiKey,
  updateApiKey,
  UserProfile,
  ApiKey,
  ApiKeyWithSecret,
  COMMON_CURRENCIES,
  COMMON_TIMEZONES,
} from '@/lib/settings'
import { useRouter } from 'next/navigation'

type TabType = 'profile' | 'currency' | 'theme' | 'notifications' | 'api-keys'

export default function SettingsPage() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<TabType>('profile')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  // User Profile State
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [profileForm, setProfileForm] = useState({
    first_name: '',
    last_name: '',
    timezone: 'UTC',
  })

  // Password Change State
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })

  // Currency State
  const [selectedCurrency, setSelectedCurrency] = useState('USD')

  // Theme State
  const [selectedTheme, setSelectedTheme] = useState<'light' | 'dark' | 'auto'>('auto')

  // API Keys State
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [showNewKeyDialog, setShowNewKeyDialog] = useState(false)
  const [newKeyForm, setNewKeyForm] = useState({
    name: '',
    description: '',
    permissions: 'read',
  })
  const [newlyCreatedKey, setNewlyCreatedKey] = useState<ApiKeyWithSecret | null>(null)

  useEffect(() => {
    loadProfile()
    loadApiKeys()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const loadProfile = async () => {
    try {
      setLoading(true)
      const data = await getUserProfile()
      setProfile(data)
      setProfileForm({
        first_name: data.first_name || '',
        last_name: data.last_name || '',
        timezone: data.timezone,
      })
      setSelectedCurrency(data.preferred_currency)
      setSelectedTheme(data.theme as 'light' | 'dark' | 'auto')
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to load profile')
      if (error.response?.status === 401) {
        router.push('/auth/login')
      }
    } finally {
      setLoading(false)
    }
  }

  const loadApiKeys = async () => {
    try {
      const keys = await getApiKeys()
      setApiKeys(keys)
    } catch (error: any) {
      console.error('Failed to load API keys:', error)
    }
  }

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text })
    setTimeout(() => setMessage(null), 5000)
  }

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setSaving(true)
      await updateUserProfile(profileForm)
      showMessage('success', 'Profile updated successfully')
      await loadProfile()
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault()
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      showMessage('error', 'New passwords do not match')
      return
    }
    try {
      setSaving(true)
      await changePassword({
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password,
      })
      showMessage('success', 'Password changed successfully')
      setPasswordForm({
        current_password: '',
        new_password: '',
        confirm_password: '',
      })
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to change password')
    } finally {
      setSaving(false)
    }
  }

  const handleCurrencyUpdate = async () => {
    try {
      setSaving(true)
      await updateUserProfile({ preferred_currency: selectedCurrency })
      showMessage('success', 'Currency preference updated')
      await loadProfile()
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to update currency')
    } finally {
      setSaving(false)
    }
  }

  const handleThemeUpdate = async (theme: 'light' | 'dark' | 'auto') => {
    try {
      setSaving(true)
      setSelectedTheme(theme)
      await updateUserProfile({ theme })
      showMessage('success', 'Theme preference updated')
      await loadProfile()
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to update theme')
      setSelectedTheme(profile?.theme as 'light' | 'dark' | 'auto')
    } finally {
      setSaving(false)
    }
  }

  const handleCreateApiKey = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setSaving(true)
      const newKey = await createApiKey(newKeyForm)
      setNewlyCreatedKey(newKey)
      setNewKeyForm({ name: '', description: '', permissions: 'read' })
      await loadApiKeys()
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to create API key')
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteApiKey = async (keyId: number) => {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      return
    }
    try {
      await deleteApiKey(keyId)
      showMessage('success', 'API key deleted')
      await loadApiKeys()
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to delete API key')
    }
  }

  const handleToggleApiKey = async (key: ApiKey) => {
    try {
      await updateApiKey(key.id, { is_active: !key.is_active })
      showMessage('success', `API key ${key.is_active ? 'disabled' : 'enabled'}`)
      await loadApiKeys()
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to update API key')
    }
  }

  const tabs = [
    { id: 'profile' as TabType, name: 'Profile', icon: '👤' },
    { id: 'currency' as TabType, name: 'Currency', icon: '💱' },
    { id: 'theme' as TabType, name: 'Theme', icon: '🎨' },
    { id: 'notifications' as TabType, name: 'Notifications', icon: '🔔' },
    { id: 'api-keys' as TabType, name: 'API Keys', icon: '🔑' },
  ]

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500 dark:text-gray-400">Loading settings...</div>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Manage your account and application preferences
          </p>
        </div>

        {message && (
          <div
            className={`p-4 rounded-lg ${
              message.type === 'success'
                ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200'
                : 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200'
            }`}
          >
            {message.text}
          </div>
        )}

        {/* Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2`}
              >
                <span>{tab.icon}</span>
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Profile Information
                </h3>
                <form onSubmit={handleProfileUpdate} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        First Name
                      </label>
                      <input
                        type="text"
                        value={profileForm.first_name}
                        onChange={(e) =>
                          setProfileForm({ ...profileForm, first_name: e.target.value })
                        }
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Last Name
                      </label>
                      <input
                        type="text"
                        value={profileForm.last_name}
                        onChange={(e) =>
                          setProfileForm({ ...profileForm, last_name: e.target.value })
                        }
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Email
                    </label>
                    <input
                      type="email"
                      value={profile?.email || ''}
                      disabled
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-100 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed"
                    />
                    <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                      Email cannot be changed
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Timezone
                    </label>
                    <select
                      value={profileForm.timezone}
                      onChange={(e) =>
                        setProfileForm({ ...profileForm, timezone: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    >
                      {COMMON_TIMEZONES.map((tz) => (
                        <option key={tz} value={tz}>
                          {tz}
                        </option>
                      ))}
                    </select>
                  </div>

                  <button
                    type="submit"
                    disabled={saving}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {saving ? 'Saving...' : 'Save Profile'}
                  </button>
                </form>
              </div>

              <hr className="border-gray-200 dark:border-gray-700" />

              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Change Password
                </h3>
                <form onSubmit={handlePasswordChange} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Current Password
                    </label>
                    <input
                      type="password"
                      value={passwordForm.current_password}
                      onChange={(e) =>
                        setPasswordForm({ ...passwordForm, current_password: e.target.value })
                      }
                      required
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      New Password
                    </label>
                    <input
                      type="password"
                      value={passwordForm.new_password}
                      onChange={(e) =>
                        setPasswordForm({ ...passwordForm, new_password: e.target.value })
                      }
                      required
                      minLength={8}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    />
                    <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                      Min 8 characters, must contain uppercase, lowercase, and digit
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Confirm New Password
                    </label>
                    <input
                      type="password"
                      value={passwordForm.confirm_password}
                      onChange={(e) =>
                        setPasswordForm({ ...passwordForm, confirm_password: e.target.value })
                      }
                      required
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={saving}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {saving ? 'Changing...' : 'Change Password'}
                  </button>
                </form>
              </div>
            </div>
          )}

          {/* Currency Tab */}
          {activeTab === 'currency' && (
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Preferred Currency
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  Select your preferred currency for displaying financial data
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {COMMON_CURRENCIES.map((currency) => (
                  <button
                    key={currency.code}
                    onClick={() => setSelectedCurrency(currency.code)}
                    className={`p-4 border-2 rounded-lg text-left transition-colors ${
                      selectedCurrency === currency.code
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-semibold text-gray-900 dark:text-white">
                          {currency.code}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                          {currency.name}
                        </div>
                      </div>
                      <div className="text-2xl">{currency.symbol}</div>
                    </div>
                  </button>
                ))}
              </div>

              {selectedCurrency !== profile?.preferred_currency && (
                <button
                  onClick={handleCurrencyUpdate}
                  disabled={saving}
                  className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving ? 'Saving...' : 'Save Currency Preference'}
                </button>
              )}
            </div>
          )}

          {/* Theme Tab */}
          {activeTab === 'theme' && (
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Theme Preference
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  Choose your preferred color theme
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  { value: 'light' as const, label: 'Light', icon: '☀️', desc: 'Light mode' },
                  { value: 'dark' as const, label: 'Dark', icon: '🌙', desc: 'Dark mode' },
                  { value: 'auto' as const, label: 'Auto', icon: '🔄', desc: 'System default' },
                ].map((theme) => (
                  <button
                    key={theme.value}
                    onClick={() => handleThemeUpdate(theme.value)}
                    disabled={saving}
                    className={`p-6 border-2 rounded-lg text-center transition-colors ${
                      selectedTheme === theme.value
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    <div className="text-4xl mb-2">{theme.icon}</div>
                    <div className="font-semibold text-gray-900 dark:text-white">
                      {theme.label}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">{theme.desc}</div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Notifications Tab */}
          {activeTab === 'notifications' && (
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Notification Preferences
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  Notification preferences will be available soon. You&apos;ll be able to configure email,
                  Telegram, and webhook notifications.
                </p>
              </div>
              <div className="p-8 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-center">
                <div className="text-4xl mb-4">🔔</div>
                <p className="text-gray-600 dark:text-gray-400">
                  Notification settings coming soon
                </p>
              </div>
            </div>
          )}

          {/* API Keys Tab */}
          {activeTab === 'api-keys' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">API Keys</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Manage API keys for external integrations
                  </p>
                </div>
                <button
                  onClick={() => {
                    setShowNewKeyDialog(true)
                    setNewlyCreatedKey(null)
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Create API Key
                </button>
              </div>

              {/* New Key Dialog */}
              {showNewKeyDialog && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
                    {newlyCreatedKey ? (
                      <div className="space-y-4">
                        <h4 className="text-lg font-semibold text-gray-900 dark:text-white">
                          API Key Created
                        </h4>
                        <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                          <p className="text-sm text-yellow-800 dark:text-yellow-200 font-semibold mb-2">
                            ⚠️ Save this key now! It won&apos;t be shown again.
                          </p>
                          <div className="mt-2 p-2 bg-white dark:bg-gray-900 rounded font-mono text-sm break-all">
                            {newlyCreatedKey.key}
                          </div>
                        </div>
                        <button
                          onClick={() => {
                            setShowNewKeyDialog(false)
                            setNewlyCreatedKey(null)
                          }}
                          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                        >
                          Done
                        </button>
                      </div>
                    ) : (
                      <form onSubmit={handleCreateApiKey} className="space-y-4">
                        <h4 className="text-lg font-semibold text-gray-900 dark:text-white">
                          Create New API Key
                        </h4>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Name *
                          </label>
                          <input
                            type="text"
                            value={newKeyForm.name}
                            onChange={(e) =>
                              setNewKeyForm({ ...newKeyForm, name: e.target.value })
                            }
                            required
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                            placeholder="My Integration"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Description
                          </label>
                          <textarea
                            value={newKeyForm.description}
                            onChange={(e) =>
                              setNewKeyForm({ ...newKeyForm, description: e.target.value })
                            }
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                            rows={3}
                            placeholder="Optional description"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Permissions
                          </label>
                          <select
                            value={newKeyForm.permissions}
                            onChange={(e) =>
                              setNewKeyForm({ ...newKeyForm, permissions: e.target.value })
                            }
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                          >
                            <option value="read">Read Only</option>
                            <option value="write">Read & Write</option>
                            <option value="admin">Admin</option>
                          </select>
                        </div>

                        <div className="flex gap-2">
                          <button
                            type="button"
                            onClick={() => {
                              setShowNewKeyDialog(false)
                              setNewKeyForm({ name: '', description: '', permissions: 'read' })
                            }}
                            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                          >
                            Cancel
                          </button>
                          <button
                            type="submit"
                            disabled={saving}
                            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                          >
                            {saving ? 'Creating...' : 'Create'}
                          </button>
                        </div>
                      </form>
                    )}
                  </div>
                </div>
              )}

              {/* API Keys List */}
              <div className="space-y-3">
                {apiKeys.length === 0 ? (
                  <div className="p-8 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-center">
                    <div className="text-4xl mb-4">🔑</div>
                    <p className="text-gray-600 dark:text-gray-400">
                      No API keys yet. Create one to get started.
                    </p>
                  </div>
                ) : (
                  apiKeys.map((key) => (
                    <div
                      key={key.id}
                      className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h4 className="font-semibold text-gray-900 dark:text-white">
                              {key.name}
                            </h4>
                            <span
                              className={`px-2 py-1 text-xs rounded ${
                                key.is_active
                                  ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
                                  : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'
                              }`}
                            >
                              {key.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </div>
                          {key.description && (
                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                              {key.description}
                            </p>
                          )}
                          <div className="mt-2 flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                            <span className="font-mono">{key.key_prefix}...</span>
                            <span>Permissions: {key.permissions}</span>
                            <span>Created: {new Date(key.created_at).toLocaleDateString()}</span>
                            {key.last_used_at && (
                              <span>
                                Last used: {new Date(key.last_used_at).toLocaleDateString()}
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleToggleApiKey(key)}
                            className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-50 dark:hover:bg-gray-700"
                          >
                            {key.is_active ? 'Disable' : 'Enable'}
                          </button>
                          <button
                            onClick={() => handleDeleteApiKey(key.id)}
                            className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  )
}
