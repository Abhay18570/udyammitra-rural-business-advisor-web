import { useAdminData } from './useAdminData'
import { Link, useNavigate } from 'react-router-dom'
import { useUi } from '../../i18n/uiContextValue'
import { statePath, type StateAnalytics } from '../../services/adminService'
import { AdminDataFeedback, GeographicSummary } from './AdminData'
import { GeographyChart } from './GeographyChart'

export function StateAnalyticsView({ data }: { data: StateAnalytics }) {
  const { text } = useUi()
  const navigate = useNavigate()
  return <>
    <GeographicSummary cards={[[ 'Profiled Entrepreneurs', data.total_entrepreneurs], ['States Represented', data.states_count], ['Districts Represented', data.districts_count]]} />
    {data.missing_state_count > 0 && <p className="officer-notice">{text('Some entrepreneur profiles do not have state information.')} ({data.missing_state_count})</p>}
    {!data.states.length ? <p className="officer-notice">{text('No entrepreneur location data is available yet.')}</p> : <>
      <GeographyChart title="Entrepreneurs by State" axis="State" rows={data.states.map(row => ({ ...row, name: row.state, key: row.state_key }))} onSelect={key => navigate(statePath(key))} />
      <p>{text('Share is based on profiles with a provided location.')}</p>
      <div className="officer-scroll" tabIndex={0} role="region" aria-label={text('Entrepreneurs by State')}><table className="officer-table"><caption>{text('Entrepreneurs by State')}</caption><thead><tr>{['State','Entrepreneurs','Share','Districts','New Enterprises','Existing Enterprises','Action'].map(label => <th scope="col" key={label}>{text(label)}</th>)}</tr></thead><tbody>{data.states.map(row => <tr key={row.state_key}><th scope="row">{row.state}</th><td>{row.entrepreneur_count}</td><td>{row.percentage}%</td><td>{row.districts_count}</td><td>{row.new_enterprises}</td><td>{row.existing_enterprises}</td><td><Link to={statePath(row.state_key)} aria-label={`${text('View Districts')}: ${row.state}`}>{text('View Districts')}</Link></td></tr>)}</tbody></table></div>
    </>}
  </>
}
export function GeographicAnalyticsPage() {
  const { text } = useUi()
  const { state, retry } = useAdminData<StateAnalytics>('analytics/states')
  return <section><h1>{text('Geographic Analytics')}</h1><p>{text('State and district distribution of registered entrepreneurs')}</p><AdminDataFeedback state={state} retry={retry} error="Unable to load geographic analytics." />{state.status === 'ready' && <StateAnalyticsView data={state.data} />}</section>
}
