export interface User {
  id: string
  email: string
  full_name?: string
  role: 'user' | 'premium' | 'admin'
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface RegisterRequest {
  email: string
  password: string
  full_name?: string
}

export interface RegisterResponse {
  message: string
  user: User
}

export interface ResetPasswordRequest {
  email: string
}

export interface ResetPasswordResponse {
  message: string
}

export interface ConfirmResetPasswordRequest {
  token: string
  new_password: string
}

export interface VerifyEmailRequest {
  token: string
}

export interface VerifyEmailResponse {
  message: string
}

export interface AuthError {
  detail: string
}
