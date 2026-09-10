import { ProtectedRoute } from './ProtectedRoute'

export function AdminProtectedRoute() {
  return <ProtectedRoute roles={['ADMIN', 'SUPER_ADMIN']} />
}
