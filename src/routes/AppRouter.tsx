import { useUi as useTextUi } from '../i18n/uiContextValue'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AdminLayout } from '../layouts/AdminLayout'
import { AuthLayout } from '../layouts/AuthLayout'
import { PublicLayout } from '../layouts/PublicLayout'
import { UserDashboardLayout } from '../layouts/UserDashboardLayout'
import { ForgotPasswordPage } from '../pages/auth/ForgotPasswordPage'
import { LoginPage } from '../pages/auth/LoginPage'
import { RegisterPage } from '../pages/auth/RegisterPage'
import { PlaceholderPage } from '../pages/PlaceholderPage'
import { HomePage } from '../pages/public/HomePage'
import { ProtectedRoute } from './ProtectedRoute'
import { OnboardingPage } from '../features/onboarding/OnboardingPage'
import { DashboardPage } from '../features/dashboard/DashboardPage'
import { ProfilePage } from '../pages/user/ProfilePage'
import { BusinessCatalogPage } from '../features/businessCatalog/BusinessCatalogPage'
import { BusinessDetailPage } from '../features/businessCatalog/BusinessDetailPage'
import { MarketAnalysisPage } from '../features/marketAnalysis/MarketAnalysisPage'
import { BusinessAnalysisPage } from '../features/businessAnalysis/BusinessAnalysisPage'
import { GovernmentSchemesPage } from '../features/schemes/GovernmentSchemesPage'
import { FinancialPlanPage } from '../features/financial/FinancialPlanPage'

const publicPages = ['about', 'how-it-works', 'features', 'privacy', 'terms', 'disclaimer']
const userPages = ['documents', 'compliance', 'advisor', 'compare', 'my-analyses', 'reports', 'notifications', 'settings']
const adminPages = ['dashboard', 'users', 'businesses', 'schemes', 'knowledge', 'map', 'reports', 'settings']

export function AppRouter() {
  const { text: textUi } = useTextUi()

  return (
    <BrowserRouter>
      <Routes>
        <Route element={<PublicLayout />}>
          <Route index element={<HomePage />} />
          {publicPages.map(path => <Route key={path} path={path} element={<PlaceholderPage area="UdyamMitra" />} />)}
        </Route>
        <Route element={<AuthLayout />}>
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
          <Route path="forgot-password" element={<ForgotPasswordPage />} />
        </Route>
        <Route element={<ProtectedRoute roles={['USER', 'ADMIN', 'SUPER_ADMIN']} />}>
          <Route element={<UserDashboardLayout />}>
            <Route path="schemes" element={<GovernmentSchemesPage />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="onboarding" element={<OnboardingPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="market-analysis" element={<MarketAnalysisPage />} />
            <Route path="opportunities" element={<BusinessCatalogPage />} />
            <Route path="opportunities/:businessId" element={<BusinessDetailPage />} />
            <Route path="business-analysis" element={<BusinessAnalysisPage />} />
            <Route path="business-health" element={<Navigate to="/business-analysis" replace />} />
            <Route path="financial-plan" element={<FinancialPlanPage />} />
            <Route path="financial-plan/:businessId" element={<FinancialPlanPage />} />
            {userPages.map(path => <Route key={path} path={path} element={<PlaceholderPage area="Entrepreneur workspace" />} />)}
            <Route path="financial-plan/:businessId/stress-test" element={<PlaceholderPage title={textUi("Financial Stress Test")} area="Entrepreneur workspace" />} />
            <Route path="reports/:reportId" element={<PlaceholderPage title={textUi("Feasibility Report")} area="Entrepreneur workspace" />} />
          </Route>
        </Route>
        <Route path="admin/login" element={<AuthLayout />}>
          <Route index element={<LoginPage />} />
        </Route>
        <Route element={<ProtectedRoute roles={['ADMIN', 'SUPER_ADMIN']} />}>
          <Route path="admin" element={<AdminLayout />}>
            {adminPages.map(path => <Route key={path} path={path} element={<PlaceholderPage area="Administration" />} />)}
            <Route index element={<Navigate to="dashboard" replace />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
