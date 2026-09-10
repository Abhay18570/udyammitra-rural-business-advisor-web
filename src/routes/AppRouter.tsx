import { lazy, Suspense } from 'react'
import { useUi as useTextUi } from '../i18n/uiContextValue'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AdminDashboardLayout } from '../layouts/AdminDashboardLayout'
import { AdminDashboardPage } from '../features/admin/AdminDashboardPage'
import { AdminProtectedRoute } from './AdminProtectedRoute'
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
import { GovernmentSchemeCatalogPage } from '../features/governmentSchemes/GovernmentSchemeCatalogPage'
import { GovernmentSchemeDetailPage } from '../features/governmentSchemes/GovernmentSchemeDetailPage'
import { FinancialPlanPage } from '../features/financial/FinancialPlanPage'

const GeographicAnalyticsPage = lazy(() => import('../features/admin/GeographicAnalyticsPage').then(module => ({ default: module.GeographicAnalyticsPage })))
const StateAnalyticsPage = lazy(() => import('../features/admin/StateAnalyticsPage').then(module => ({ default: module.StateAnalyticsPage })))
const EntrepreneursPage = lazy(() => import('../features/admin/EntrepreneursPage').then(module => ({ default: module.EntrepreneursPage })))

const publicPages = ['about', 'how-it-works', 'features', 'privacy', 'terms', 'disclaimer']
const userPages = ['documents', 'compliance', 'advisor', 'compare', 'my-analyses', 'reports', 'notifications', 'settings']

export function AppRouter() {
  const { text: textUi } = useTextUi()

  return (
    <BrowserRouter>
      <Routes>
        <Route element={<PublicLayout />}>
          <Route index element={<HomePage />} />
          <Route path="government-schemes" element={<GovernmentSchemeCatalogPage />} />
          <Route path="government-schemes/:slug" element={<GovernmentSchemeDetailPage />} />
          {publicPages.map(path => <Route key={path} path={path} element={<PlaceholderPage area="UdyamMitra" />} />)}
        </Route>
        <Route element={<AuthLayout />}>
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
          <Route path="forgot-password" element={<ForgotPasswordPage />} />
        </Route>
        <Route element={<ProtectedRoute roles={['USER']} />}>
          <Route element={<UserDashboardLayout />}>
            <Route path="schemes" element={<GovernmentSchemeCatalogPage />} />
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
        <Route element={<AdminProtectedRoute />}>
          <Route path="admin" element={<AdminDashboardLayout />}>
            <Route path="dashboard" element={<AdminDashboardPage />} />
            <Route path="analytics/geography" element={<Suspense fallback={<p role="status">{textUi("Loading statistics")}</p>}><GeographicAnalyticsPage /></Suspense>} />
            <Route path="analytics/geography/state/:stateKey" element={<Suspense fallback={<p role="status">{textUi("Loading statistics")}</p>}><StateAnalyticsPage /></Suspense>} />
            <Route path="entrepreneurs" element={<Suspense fallback={<p role="status">{textUi("Loading statistics")}</p>}><EntrepreneursPage /></Suspense>} />
            <Route index element={<Navigate to="dashboard" replace />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
