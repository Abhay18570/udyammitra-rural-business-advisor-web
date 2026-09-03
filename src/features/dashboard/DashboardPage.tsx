import { AlertCircle, LoaderCircle } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '../../components/ui/Button'
import { getApiErrorMessage } from '../../services/apiError'
import { profileService } from '../../services/profileService'
import { marketService } from '../../services/marketService'
import { feasibilityService } from '../../services/feasibilityService'
import type { FeasibilityAnalysis } from '../../types/feasibility'
import type { EntrepreneurProfile } from '../../types/profile'
import { DashboardHeader } from './DashboardHeader'
import { AnalysisEmptyStates, CurrentBusinessCard, PrimaryJourney, RecentActivity } from './DashboardPanels'
import { JourneyProgress } from './JourneyProgress'
import { ProfileSnapshot } from './ProfileSnapshot'
import { QuickActions } from './QuickActions'

export function DashboardPage() {
  const navigate = useNavigate(); const [profile, setProfile] = useState<EntrepreneurProfile | null>(null); const [loading, setLoading] = useState(true); const [error, setError] = useState(''); const [latestMarketDate, setLatestMarketDate] = useState<string>(); const [feasibility, setFeasibility] = useState<FeasibilityAnalysis | null>(null)
  const handleProfile = useCallback((result: EntrepreneurProfile | null) => { if (!result?.onboardingCompleted) { navigate('/onboarding', { replace: true }); return } setProfile(result) }, [navigate])
  const handleError = useCallback((reason: unknown) => setError(getApiErrorMessage(reason, "We couldn't load your profile.")), [])
  const loadProfile = useCallback(() => profileService.get().then(handleProfile).catch(handleError).finally(() => setLoading(false)), [handleError, handleProfile])
  const retry = () => { setLoading(true); setError(''); void loadProfile() }
  useEffect(() => { void profileService.get().then(handleProfile).catch(handleError).finally(() => setLoading(false)); void marketService.latest().then(result => setLatestMarketDate(result?.createdAt)).catch(() => undefined); void feasibilityService.latest().then(setFeasibility).catch(() => undefined) }, [handleError, handleProfile])
  if (loading) return <div className="entrepreneur-dashboard"><div className="dashboard-loading" role="status"><LoaderCircle className="dashboard-spinner" aria-hidden="true" /><span>Loading your entrepreneur workspace…</span></div><div className="dashboard-skeleton" aria-hidden="true"><i /><i /><i /><i /></div></div>
  if (error || !profile) return <div className="entrepreneur-dashboard"><section className="dashboard-error" role="alert"><AlertCircle aria-hidden="true" /><h1>We couldn't load your profile.</h1><p>{error || 'Please try again.'}</p><div><Button type="button" onClick={retry}>Retry</Button><Link className="button button--outline" to="/profile">Go to Profile</Link></div></section></div>
  return <div className="entrepreneur-dashboard"><DashboardHeader profile={profile} /><PrimaryJourney profile={profile} /><ProfileSnapshot profile={profile} /><QuickActions profile={profile} /><div className="dashboard-two-column"><CurrentBusinessCard profile={profile} /><JourneyProgress /></div><AnalysisEmptyStates marketAnalysisDate={latestMarketDate} feasibility={feasibility} /><RecentActivity /></div>
}
