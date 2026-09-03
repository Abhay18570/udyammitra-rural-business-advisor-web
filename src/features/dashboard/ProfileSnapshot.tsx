import { CheckCircle2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { EntrepreneurProfile } from '../../types/profile'
import { capitalRange, formatCurrency, locationLabel, selectionLabel } from './dashboardFormatters'

export function ProfileSnapshot({ profile }: { profile: EntrepreneurProfile }) {
  const skills = profile.skills.slice(0, 3).map(selectionLabel)
  const resources = profile.resources.slice(0, 3).map(selectionLabel)
  return <div className="dashboard-profile-grid"><section className="dashboard-card profile-complete-card" aria-labelledby="profile-complete-title"><div className="profile-complete__top"><span><CheckCircle2 aria-hidden="true" /></span><div><h2 id="profile-complete-title">Profile Complete</h2><p>{profile.skills.length} skills selected · {profile.resources.length} resources selected</p></div><strong>100%</strong></div><div className="completion-track" aria-label="Profile completion: 100 percent"><i /></div><Link to="/profile">Update Profile</Link></section>
  <section className="dashboard-card profile-snapshot" aria-labelledby="snapshot-title"><div className="card-heading-row"><h2 id="snapshot-title">Your Profile Snapshot</h2><Link to="/profile">View Full Profile</Link></div><dl><div><dt>Location</dt><dd>{locationLabel(profile)}</dd></div><div><dt>Capital range</dt><dd>{capitalRange(profile)}</dd></div><div><dt>Own capital</dt><dd>{formatCurrency(profile.ownCapital)}</dd></div><div><dt>Loan required</dt><dd>{formatCurrency(profile.loanRequired)}</dd></div><div><dt>Top skills</dt><dd>{skills.join(', ') || 'None selected'}</dd></div><div><dt>Available resources</dt><dd>{resources.join(', ') || 'None selected'}</dd></div><div><dt>Current business</dt><dd>{profile.hasExistingBusiness ? profile.existingBusiness?.businessName || 'Existing business' : 'No current business'}</dd></div></dl></section></div>
}
