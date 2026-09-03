import { createContext, useContext } from 'react'
import type { AuthUser, LoginRequest, RegisterRequest } from '../types/auth'

export type AuthContextValue = { user: AuthUser | null; isAuthenticated: boolean; isLoading: boolean; login: (request: LoginRequest) => Promise<AuthUser>; register: (request: RegisterRequest) => Promise<AuthUser>; logout: () => void }
export const AuthContext = createContext<AuthContextValue | null>(null)
export function useAuth(): AuthContextValue { const context = useContext(AuthContext); if (!context) throw new Error('useAuth must be used within AuthProvider.'); return context }
