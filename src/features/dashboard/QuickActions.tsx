import { useUi as useTextUi } from '../../i18n/uiContextValue'
import { LocalizedText } from '../../i18n/LocalizedText'
import { BarChart3, BriefcaseBusiness, Building2, Calculator, FileCheck2, FileText, HeartPulse, MessageSquareText } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { EntrepreneurProfile } from '../../types/profile'

interface ActionItem {
  title: string
  to?: string
  description: string
  icon: typeof BarChart3
  businessOnly?: boolean
  disabled?: boolean
  planned?: boolean
}

const actions: ActionItem[] = [
  { title: 'Local Market Analysis', to: '/market-analysis', description: 'Understand demand, competition and nearby business activity.', icon: BarChart3 },
  { title: 'Business Opportunities', to: '/opportunities', description: 'Discover businesses that fit your profile, capital and local market.', icon: BriefcaseBusiness },
  { title: 'Existing Business Health', to: '/business-health', description: 'Review the health and future potential of your current business.', icon: HeartPulse, businessOnly: true },
  { title: 'Financial Planner', to: '/financial-plan', description: 'Convert your available margin capital into an indicative project-cost structure.', icon: Calculator },
  { title: 'Government Schemes', to: '/schemes', description: 'Explore scheme guidance and future eligibility matches.', icon: Building2 },
  { title: 'Documentation', to: '/documents', description: 'Review documents and registration guidance.', icon: FileCheck2 },
  { title: 'AI Advisor', to: '/advisor', description: 'Ask questions about your analysis and next steps.', icon: MessageSquareText, planned: true },
  { title: 'Reports', to: '/reports', description: 'View saved feasibility reports.', icon: FileText },
]

export function QuickActions({ profile }: { profile: EntrepreneurProfile }) {
  const { text: textUi } = useTextUi()

  return <section className="dashboard-section" aria-labelledby="quick-actions-title"><div className="dashboard-section__heading"><div><span className="eyebrow"><LocalizedText value={"Workspace"} /></span><h2 id="quick-actions-title"><LocalizedText value={"Quick actions"} /></h2></div></div><div className="quick-action-grid">{actions.map(({ title, to, description, icon: Icon, disabled, planned, businessOnly }) => {
    const subdued = businessOnly && !profile.hasExistingBusiness
    const content = <><span className="quick-action__icon"><Icon aria-hidden="true" /></span><span className="quick-action__copy"><strong><LocalizedText value={title} /></strong><p><LocalizedText value={subdued ? 'Add an existing business to your profile to use this analysis.' : description} /></p></span>{planned && <small className="status-label"><LocalizedText value={"Not yet active"} /></small>}{disabled && <small className="status-label"><LocalizedText value={"Coming later"} /></small>}</>
    return disabled ? <div key={title} className="quick-action quick-action--disabled" aria-disabled="true">{content}</div> : <Link key={title} className={subdued ? 'quick-action quick-action--subdued' : 'quick-action'} to={to!} aria-label={textUi(`${title}: ${subdued ? 'add a business to your profile first' : description}`)}>{content}</Link>
  })}</div></section>
}
