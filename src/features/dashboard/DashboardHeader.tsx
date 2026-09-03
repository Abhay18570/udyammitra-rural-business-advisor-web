import { BriefcaseBusiness, IndianRupee, MapPin } from 'lucide-react'
import type { EntrepreneurProfile } from '../../types/profile'
import { capitalRange, locationLabel } from './dashboardFormatters'

export function DashboardHeader({ profile }: { profile: EntrepreneurProfile }) {
  const existing = profile.hasExistingBusiness === true
  return <header className="dashboard-welcome">
    <div><span className="eyebrow">Entrepreneur workspace</span><h1>Welcome back, {profile.fullName.trim().split(/\s+/)[0]}</h1><p>Continue building your business feasibility analysis.</p></div>
    <div className="dashboard-context" aria-label="Profile context">
      <div><MapPin aria-hidden="true" /><span><small>Location</small><strong>{locationLabel(profile)}</strong></span></div>
      <div><IndianRupee aria-hidden="true" /><span><small>Capital</small><strong>{capitalRange(profile)}</strong></span></div>
      <div><BriefcaseBusiness aria-hidden="true" /><span><small>Profile type</small><strong>{existing ? 'Existing Entrepreneur' : 'Aspiring Entrepreneur'}</strong></span></div>
    </div>
  </header>
}
