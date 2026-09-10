import { useEffect, useState } from 'react'
import { isAxiosError } from 'axios'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/authContextValue'
import { useUi } from '../../i18n/uiContextValue'
import { getAdminOverview, type AdminOverview } from '../../services/adminService'

const metrics: Array<[keyof AdminOverview, string, string]> = [
  ['total_registered_users', 'Total Registered Users', 'Entrepreneur user accounts registered on UdyamMitra'],
  ['total_entrepreneurs', 'Total Entrepreneurs', 'Registered users who have created an entrepreneur profile'],
  ['profiles_pending', 'Profiles Pending', 'Registered users who have not created an entrepreneur profile'],
  ['new_enterprises', 'New Enterprises', 'Profiles marked as new enterprises'],
  ['existing_enterprises', 'Existing Enterprises', 'Profiles marked as existing enterprises'],
  ['states_count', 'States Represented', 'Distinct states provided in entrepreneur profiles'],
  ['districts_count', 'Districts Represented', 'Distinct state and district pairs provided in profiles'],
]
export type OverviewState = { status: 'loading' } | { status: 'error'; forbidden: boolean } | { status: 'ready'; data: AdminOverview }

export function AdminOverviewView({ state, retry }: { state: OverviewState; retry: () => void }) {
  const { text, language } = useUi()
  return <section aria-labelledby="overview-heading">
    <h1 id="overview-heading">{text('Entrepreneurship Overview')}</h1>
    <p>{text('Monitor registered entrepreneurs and entrepreneurship activity across UdyamMitra.')}</p>
    <Link className="officer-dashboard-link" to="/admin/analytics/geography">{text('View Geographic Analytics')}</Link>
    {state.status === 'loading' ? <div role="status" aria-label={text('Loading statistics')} aria-busy="true"><p>{text('Loading statistics')}</p><div className="officer-kpis">{metrics.map(([key, title]) => <div key={key} className="officer-card officer-skeleton" aria-hidden="true"><h2>{text(title)}</h2><span /></div>)}</div></div>
      : state.status === 'error' ? <div role="alert" className="officer-notice"><p>{text(state.forbidden ? 'You do not have permission to access the administration portal.' : 'Unable to load entrepreneurship statistics.')}</p>{!state.forbidden && <button onClick={retry}>{text('Try again')}</button>}</div>
      : <>{state.data.total_registered_users === 0 ? <p className="officer-notice">{text('No entrepreneurs have registered yet.')}</p> : state.data.total_entrepreneurs === 0 && <p className="officer-notice">{text('Registered users have not created entrepreneur profiles yet.')}</p>}
        <div className="officer-kpis">{metrics.map(([key, title, explanation]) => <article className="officer-card" key={key}><h2>{text(title)}</h2><strong>{new Intl.NumberFormat(`${language}-IN`).format(state.data[key])}</strong><p>{text(explanation)}</p></article>)}</div>
        <p className="officer-footnote">{text('Administrator accounts are excluded. Enterprise status may be unclassified. Pending means no profile has been created.')}</p>
      </>}
  </section>
}

export function AdminDashboardPage() {
  const [state, setState] = useState<OverviewState>({ status: 'loading' })
  const [revision, setRevision] = useState(0)
  const { logout } = useAuth()
  const navigate = useNavigate()
  useEffect(() => {
    const controller = new AbortController()
    getAdminOverview(controller.signal).then(data => {
      if (!controller.signal.aborted) setState({ status: 'ready', data })
    }).catch(error => {
      if (controller.signal.aborted) return
      if (isAxiosError(error) && error.response?.status === 401) {
        logout(); navigate('/login', { replace: true }); return
      }
      setState({ status: 'error', forbidden: isAxiosError(error) && error.response?.status === 403 })
    })
    return () => controller.abort()
  }, [revision, logout, navigate])
  return <AdminOverviewView state={state} retry={() => { setState({ status: 'loading' }); setRevision(value => value + 1) }} />
}
