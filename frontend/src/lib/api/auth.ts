import type { LoginRequest, TokenResponse, TokenVerifyResponse } from '@/types/api'
import { apiPost } from './client'

// ─── Auth API ───

export function login(data: LoginRequest, signal?: AbortSignal) {
  return apiPost<TokenResponse>('/api/v1/auth/login', data, { signal })
}

export function refreshToken(refreshToken: string, signal?: AbortSignal) {
  return apiPost<TokenResponse>('/api/v1/auth/refresh', { refresh_token: refreshToken }, { signal })
}

export function verifyToken(accessToken: string, signal?: AbortSignal) {
  return apiPost<TokenVerifyResponse>('/api/v1/auth/verify', undefined, {
    signal,
    headers: { Authorization: `Bearer ${accessToken}` }
  })
}

// ─── Token storage ───

const ACCESS_TOKEN_KEY = 'uncase-access-token'
const REFRESH_TOKEN_KEY = 'uncase-refresh-token'

export function storeTokens(accessToken: string, refreshToken: string): void {
  if (typeof window === 'undefined') return
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
}

export function getStoredAccessToken(): string | null {
  if (typeof window === 'undefined') return null

  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function getStoredRefreshToken(): string | null {
  if (typeof window === 'undefined') return null

  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function clearTokens(): void {
  if (typeof window === 'undefined') return
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}
