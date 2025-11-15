import api from './api'

export interface UserProfile {
  id: number
  uuid: string
  email: string
  first_name: string | null
  last_name: string | null
  is_active: boolean
  is_verified: boolean
  email_verified_at: string | null
  last_login_at: string | null
  preferred_currency: string
  timezone: string
  theme: string
  role: string
  created_at: string
  updated_at: string
}

export interface UserProfileUpdate {
  first_name?: string | null
  last_name?: string | null
  preferred_currency?: string
  timezone?: string
  theme?: string
}

export interface PasswordChange {
  current_password: string
  new_password: string
}

export interface NotificationPreferences {
  user_id: string
  email_enabled: boolean
  telegram_enabled: boolean
  webhook_enabled: boolean
  webpush_enabled: boolean
  email_address: string | null
  telegram_chat_id: string | null
  webhook_url: string | null
  webhook_secret: string | null
  budget_alerts_enabled: boolean
  transaction_alerts_enabled: boolean
  portfolio_alerts_enabled: boolean
  price_alerts_enabled: boolean
  system_alerts_enabled: boolean
  quiet_hours_enabled: boolean
  quiet_hours_start: string | null
  quiet_hours_end: string | null
}

export interface ApiKey {
  id: number
  uuid: string
  name: string
  description: string | null
  key_prefix: string
  permissions: string
  is_active: boolean
  last_used_at: string | null
  expires_at: string | null
  created_at: string
  updated_at: string
}

export interface ApiKeyWithSecret extends ApiKey {
  key: string
}

export interface ApiKeyCreate {
  name: string
  description?: string | null
  permissions?: string
  expires_at?: string | null
}

export interface ApiKeyUpdate {
  name?: string
  description?: string | null
  permissions?: string
  is_active?: boolean
}

// User Profile API
export const getUserProfile = async (): Promise<UserProfile> => {
  const response = await api.get('/api/v1/users/profile')
  return response.data
}

export const updateUserProfile = async (data: UserProfileUpdate): Promise<UserProfile> => {
  const response = await api.patch('/api/v1/users/profile', data)
  return response.data
}

export const changePassword = async (data: PasswordChange): Promise<void> => {
  await api.post('/api/v1/users/change-password', data)
}

// Notification Preferences API
export const getNotificationPreferences = async (userId: string): Promise<NotificationPreferences> => {
  const response = await api.get(`/api/v1/notifications/preferences/${userId}`)
  return response.data
}

export const updateNotificationPreferences = async (
  userId: string,
  data: Partial<NotificationPreferences>
): Promise<NotificationPreferences> => {
  const response = await api.put(`/api/v1/notifications/preferences/${userId}`, data)
  return response.data
}

// API Keys API
export const getApiKeys = async (): Promise<ApiKey[]> => {
  const response = await api.get('/api/v1/api-keys')
  return response.data
}

export const createApiKey = async (data: ApiKeyCreate): Promise<ApiKeyWithSecret> => {
  const response = await api.post('/api/v1/api-keys', data)
  return response.data
}

export const updateApiKey = async (keyId: number, data: ApiKeyUpdate): Promise<ApiKey> => {
  const response = await api.patch(`/api/v1/api-keys/${keyId}`, data)
  return response.data
}

export const deleteApiKey = async (keyId: number): Promise<void> => {
  await api.delete(`/api/v1/api-keys/${keyId}`)
}

// Common currencies
export const COMMON_CURRENCIES = [
  { code: 'USD', name: 'US Dollar', symbol: '$' },
  { code: 'EUR', name: 'Euro', symbol: '€' },
  { code: 'GBP', name: 'British Pound', symbol: '£' },
  { code: 'JPY', name: 'Japanese Yen', symbol: '¥' },
  { code: 'CHF', name: 'Swiss Franc', symbol: 'CHF' },
  { code: 'CAD', name: 'Canadian Dollar', symbol: 'C$' },
  { code: 'AUD', name: 'Australian Dollar', symbol: 'A$' },
  { code: 'CNY', name: 'Chinese Yuan', symbol: '¥' },
  { code: 'RON', name: 'Romanian Leu', symbol: 'RON' },
  { code: 'INR', name: 'Indian Rupee', symbol: '₹' },
]

// Common timezones
export const COMMON_TIMEZONES = [
  'UTC',
  'America/New_York',
  'America/Chicago',
  'America/Denver',
  'America/Los_Angeles',
  'Europe/London',
  'Europe/Paris',
  'Europe/Berlin',
  'Europe/Bucharest',
  'Asia/Tokyo',
  'Asia/Shanghai',
  'Asia/Kolkata',
  'Australia/Sydney',
]
