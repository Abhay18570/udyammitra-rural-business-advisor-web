import { useUi as useTextUi } from '../../i18n/uiContextValue'
import { LocalizedText } from '../../i18n/LocalizedText'
import { CheckCircle2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { EntrepreneurProfile } from '../../types/profile'
import { capitalRange, formatCurrency, locationLabel, selectionLabel } from './dashboardFormatters'

export function ProfileSnapshot({ profile }: { profile: EntrepreneurProfile }) {
  const { text: textUi } = useTextUi()

  const skills = profile.skills.slice(0, 3).map(item => item.name === 'Other' && item.otherDescription ? item.otherDescription : textUi(selectionLabel(item)))
  const resources = profile.resources.slice(0, 3).map(item => item.name === 'Other' && item.otherDescription ? item.otherDescription : textUi(selectionLabel(item)))
  return <div className="dashboard-profile-grid"><section className="dashboard-card profile-complete-card" aria-labelledby="profile-complete-title"><div className="profile-complete__top"><span><CheckCircle2 aria-hidden="true" /></span><div><h2 id="profile-complete-title"><LocalizedText value={"Profile Complete"} /></h2><p>{profile.skills.length}<LocalizedText value={" skills selected · "} />{profile.resources.length}<LocalizedText value={" resources selected"} /></p></div><strong>100%</strong></div><div className="completion-track" aria-label={textUi("Profile completion: 100 percent")}><i /></div><Link to="/profile"><LocalizedText value={"Update Profile"} /></Link></section>
  <section className="dashboard-card profile-snapshot" aria-labelledby="snapshot-title"><div className="card-heading-row"><h2 id="snapshot-title"><LocalizedText value={"Your Profile Snapshot"} /></h2><Link to="/profile"><LocalizedText value={"View Full Profile"} /></Link></div><dl><div><dt><LocalizedText value={"Location"} /></dt><dd>{locationLabel(profile)}</dd></div><div><dt><LocalizedText value={"Capital range"} /></dt><dd><LocalizedText value={capitalRange(profile)} /></dd></div><div><dt><LocalizedText value={"Own capital"} /></dt><dd>{textUi(formatCurrency(profile.ownCapital))}</dd></div><div><dt><LocalizedText value={"Loan required"} /></dt><dd>{textUi(formatCurrency(profile.loanRequired))}</dd></div><div><dt><LocalizedText value={"Top skills"} /></dt><dd>{skills.join(', ') || textUi('None selected')}</dd></div><div><dt><LocalizedText value={"Available resources"} /></dt><dd>{resources.join(', ') || textUi('None selected')}</dd></div><div><dt><LocalizedText value={"Current business"} /></dt><dd>{profile.hasExistingBusiness ? profile.existingBusiness?.businessName || textUi('Existing business') : textUi('No current business')}</dd></div></dl></section></div>
}
