import { useUi as useTextUi } from '../i18n/uiContextValue'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { LoadingState } from '../components/ui/Feedback'
import { useAuth } from '../context/authContextValue'
import type { UserRole } from '../types/auth'

export function ProtectedRoute({ roles }: { roles?: UserRole[] }) {
  const { text: textUi } = useTextUi()
 const { user, isAuthenticated, isLoading } = useAuth(); const location = useLocation(); if (isLoading) return <main className="auth-restoring"><LoadingState label={textUi("Restoring your session…")} /></main>; if (!isAuthenticated) return <Navigate to="/login" replace state={{ from: location.pathname }} />; if (roles && (!user || !roles.includes(user.role))) return <Navigate to={user?.role === 'ADMIN' || user?.role === 'SUPER_ADMIN' ? '/admin/dashboard' : '/dashboard'} replace />; return <Outlet /> }
