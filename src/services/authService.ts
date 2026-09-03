import { apiClient } from './apiClient'
import { tokenStorage } from './tokenStorage'
import type { AuthResponse, AuthUser, LoginRequest, RegisterRequest } from '../types/auth'

type ApiUser = { id: string; full_name: string; email: string; mobile_number: string; preferred_language: AuthUser['preferredLanguage']; role: AuthUser['role']; is_active: boolean }
type ApiAuthResponse = { access_token: string; token_type: 'bearer'; user: ApiUser }
const mapUser = (user: ApiUser): AuthUser => ({ id: user.id, fullName: user.full_name, email: user.email, mobile: user.mobile_number, preferredLanguage: user.preferred_language, role: user.role, isActive: user.is_active })
const mapResponse = (response: ApiAuthResponse): AuthResponse => ({ accessToken: response.access_token, tokenType: response.token_type, user: mapUser(response.user) })

export const authService = {
  async register(request: RegisterRequest): Promise<AuthResponse> {
    const { data } = await apiClient.post<ApiAuthResponse>('/auth/register', { full_name: request.fullName, email: request.email, mobile_number: request.mobile, preferred_language: request.preferredLanguage, password: request.password })
    return mapResponse(data)
  },
  async login(request: LoginRequest): Promise<AuthResponse> {
    const { data } = await apiClient.post<ApiAuthResponse>('/auth/login', { identifier: request.identifier, password: request.password })
    return mapResponse(data)
  },
  async getCurrentUser(): Promise<AuthUser> { const { data } = await apiClient.get<ApiUser>('/auth/me'); return mapUser(data) },
  logout(): void { tokenStorage.clear() },
}
