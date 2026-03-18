'use client'

import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'

import type { MembershipInfo, UserResponse } from '@/types/api'
import { isDemoMode } from '@/lib/demo'
import { getStoredAccessToken, clearTokens, storeTokens, loginWithPassword, getMe } from '@/lib/api/auth'

interface AuthUser extends UserResponse {
  role: MembershipInfo['role']
  organization_id: string
  org_name: string
}

interface AuthContextValue {
  user: AuthUser | null
  isDemo: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>
  logout: () => void
}

const DEMO_USER: AuthUser = {
  id: 'demo-user',
  email: 'demo@uncase.md',
  display_name: 'Demo User',
  is_active: true,
  created_at: new Date().toISOString(),
  role: 'owner',
  organization_id: 'demo-org',
  org_name: 'Demo Organization',
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isDemo, setIsDemo] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  const loadUser = useCallback(async () => {
    // Check demo mode first
    if (isDemoMode()) {
      setUser(DEMO_USER)
      setIsDemo(true)
      setIsLoading(false)

      return
    }

    // Check stored token
    const token = getStoredAccessToken()

    if (!token) {
      setIsLoading(false)

      return
    }

    // Fetch user profile
    const { data, error } = await getMe()

    if (data && !error) {
      const membership = data.memberships[0]

      setUser({
        ...data.user,
        role: membership?.role ?? 'viewer',
        organization_id: membership?.organization_id ?? '',
        org_name: membership?.org_name ?? '',
      })
    } else {
      // Token invalid — clear
      clearTokens()
    }

    setIsLoading(false)
  }, [])

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadUser()
  }, [loadUser])

  const loginFn = useCallback(async (email: string, password: string) => {
    const { data, error } = await loginWithPassword(email, password)

    if (error) {
      return { success: false, error: error.message }
    }

    if (data) {
      storeTokens(data.access_token, data.refresh_token)

      // Load user profile after storing tokens
      await loadUser()

      return { success: true }
    }

    return { success: false, error: 'Unknown error' }
  }, [loadUser])

  const logoutFn = useCallback(() => {
    clearTokens()
    setUser(null)
    setIsDemo(false)

    if (typeof window !== 'undefined') {
      window.location.href = '/login'
    }
  }, [])

  return (
    <AuthContext.Provider value={{ user, isDemo, isLoading, login: loginFn, logout: logoutFn }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)

  if (!ctx) throw new Error('useAuth must be used within AuthProvider')

  return ctx
}

export type { AuthUser }
