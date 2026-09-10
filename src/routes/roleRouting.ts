import type { UserRole } from '../types/auth'

export function isAdmin(role?: UserRole) { return role === 'ADMIN' || role === 'SUPER_ADMIN' }
export function loginDestination(role: UserRole, from?: string) {
  if (isAdmin(role)) return '/admin/dashboard'
  // Restore local entrepreneur paths only; never send a USER into the admin portal.
  return from?.startsWith('/') && !from.startsWith('//') && !/^\/admin(?:\/|$)/.test(from) ? from : '/dashboard'
}
