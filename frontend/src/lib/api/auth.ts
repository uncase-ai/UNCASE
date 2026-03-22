import type { LoginRequest, OrgDetailResponse, OrgMembersListResponse, RegisterRequest, TokenResponse, TokenVerifyResponse, UserMeResponse } from '@/types/api'
import { apiGet, apiPost } from './client'

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

// ─── User Management ───

export function register(data: RegisterRequest, signal?: AbortSignal) {
  return apiPost<TokenResponse>('/api/v1/auth/register', data, { signal })
}

export function loginWithPassword(email: string, password: string, signal?: AbortSignal) {
  return apiPost<TokenResponse>('/api/v1/auth/login/password', { email, password }, { signal })
}

export function getMe(signal?: AbortSignal) {
  return apiGet<UserMeResponse>('/api/v1/auth/me', { signal })
}

export function logout(): void {
  clearTokens()

  if (typeof window !== 'undefined') {
    window.location.href = '/login'
  }
}

// ─── Setup status ───

export interface SetupStatus {
  has_users: boolean
  has_organizations: boolean
  setup_complete: boolean
}

export function getSetupStatus(signal?: AbortSignal) {
  return apiGet<SetupStatus>('/health/setup', { signal })
}

// ─── Organization detail ───

export function getMyOrganization(signal?: AbortSignal) {
  return apiGet<OrgDetailResponse>('/api/v1/auth/organization', { signal })
}

export function getOrgMembers(signal?: AbortSignal) {
  return apiGet<OrgMembersListResponse>('/api/v1/auth/organization/members', { signal })
}
