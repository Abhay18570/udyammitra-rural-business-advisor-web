import { useUi as useTextUi } from '../../i18n/uiContextValue'
import { LocalizedText } from '../../i18n/LocalizedText'
import { BriefcaseBusiness, IndianRupee, MapPin } from 'lucide-react'
import type { EntrepreneurProfile } from '../../types/profile'
import { capitalRange, locationLabel } from './dashboardFormatters'

export function DashboardHeader({ profile }: { profile: EntrepreneurProfile }) {
  const { text: textUi } = useTextUi()

  const existing = profile.hasExistingBusiness === true
  return <header className="dashboard-welcome">
    <div><span className="eyebrow"><LocalizedText value={"Entrepreneur workspace"} /></span><h1><LocalizedText value={"Welcome back, "} />{profile.fullName.trim().split(/\s+/)[0]}</h1><p><LocalizedText value={"Continue building your business feasibility analysis."} /></p></div>
    <div className="dashboard-context" aria-label={textUi("Profile context")}>
      <div><MapPin aria-hidden="true" /><span><small><LocalizedText value={"Location"} /></small><strong>{locationLabel(profile)}</strong></span></div>
      <div><IndianRupee aria-hidden="true" /><span><small><LocalizedText value={"Capital"} /></small><strong><LocalizedText value={capitalRange(profile)} /></strong></span></div>
      <div><BriefcaseBusiness aria-hidden="true" /><span><small><LocalizedText value={"Profile type"} /></small><strong><LocalizedText value={existing ? 'Existing Entrepreneur' : 'Aspiring Entrepreneur'} /></strong></span></div>
    </div>
  </header>
}
