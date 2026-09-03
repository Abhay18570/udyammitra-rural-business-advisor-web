export type PreferredLanguage = 'en' | 'mr' | 'hi'
export type UserRole = 'USER' | 'ADMIN' | 'SUPER_ADMIN'
export interface LoginRequest { identifier: string; password: string; rememberMe: boolean }
export interface RegisterRequest { fullName: string; mobile: string; email: string; preferredLanguage: PreferredLanguage; password: string; termsAccepted: boolean }
export interface AuthUser { id: string; fullName: string; mobile: string; email: string; preferredLanguage: PreferredLanguage; role: UserRole; isActive: boolean }
export interface AuthResponse { user: AuthUser; accessToken: string; tokenType: 'bearer' }
