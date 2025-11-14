import api from './api'
import {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  ResetPasswordRequest,
  ResetPasswordResponse,
  ConfirmResetPasswordRequest,
  VerifyEmailRequest,
  VerifyEmailResponse,
  User,
} from '@/types/auth'

export const authService = {
  async login(data: LoginRequest): Promise<LoginResponse> {
    const formData = new FormData()
    formData.append('username', data.email)
    formData.append('password', data.password)

    const response = await api.post<LoginResponse>('/api/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    // Store tokens
    localStorage.setItem('access_token', response.data.access_token)
    localStorage.setItem('refresh_token', response.data.refresh_token)

    return response.data
  },

  async register(data: RegisterRequest): Promise<RegisterResponse> {
    const response = await api.post<RegisterResponse>('/api/v1/auth/register', data)
    return response.data
  },

  async requestPasswordReset(data: ResetPasswordRequest): Promise<ResetPasswordResponse> {
    const response = await api.post<ResetPasswordResponse>('/api/v1/auth/password-reset', data)
    return response.data
  },

  async confirmPasswordReset(data: ConfirmResetPasswordRequest): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>(
      '/api/v1/auth/password-reset/confirm',
      data
    )
    return response.data
  },

  async verifyEmail(data: VerifyEmailRequest): Promise<VerifyEmailResponse> {
    const response = await api.post<VerifyEmailResponse>('/api/v1/auth/verify-email', data)
    return response.data
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/api/v1/auth/me')
    return response.data
  },

  logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    window.location.href = '/auth/login'
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token')
  },
}

export default authService
