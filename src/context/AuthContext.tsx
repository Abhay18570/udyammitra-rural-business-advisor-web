import { useEffect, useMemo, useState, type ReactNode } from 'react'
import { authService } from '../services/authService'
import { tokenStorage } from '../services/tokenStorage'
import type { AuthUser } from '../types/auth'
import { AuthContext, type AuthContextValue } from './authContextValue'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  useEffect(() => { const restore = async () => { if (!tokenStorage.get()) { setIsLoading(false); return } try { setUser(await authService.getCurrentUser()) } catch { tokenStorage.clear(); setUser(null) } finally { setIsLoading(false) } }; void restore() }, [])
  const value = useMemo<AuthContextValue>(() => ({ user, isAuthenticated: Boolean(user), isLoading,
    login: async request => { const response = await authService.login(request); tokenStorage.set(response.accessToken, request.rememberMe); setUser(response.user); return response.user },
    register: async request => { const response = await authService.register(request); tokenStorage.set(response.accessToken); setUser(response.user); return response.user },
    logout: () => { authService.logout(); setUser(null) },
  }), [user, isLoading])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
