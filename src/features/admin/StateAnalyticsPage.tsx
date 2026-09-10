import { useAdminData } from './useAdminData'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useUi } from '../../i18n/uiContextValue'
import { entrepreneursPath, type DistrictAnalytics } from '../../services/adminService'
import { AdminDataFeedback, GeographicSummary } from './AdminData'
import { GeographyChart } from './GeographyChart'

export function DistrictAnalyticsView({ data }: { data: DistrictAnalytics }) {
  const { text } = useUi()
  const navigate = useNavigate()
  return <><h1>{data.state} — {text('Geographic Analytics')}</h1>
    <GeographicSummary cards={[[ 'Total Entrepreneurs', data.total_entrepreneurs], ['Districts Represented', data.districts_count], ['New Enterprises', data.new_enterprises], ['Existing Enterprises', data.existing_enterprises]]} />
    {data.missing_district_count > 0 && <p className="officer-notice">{text('Some entrepreneur profiles do not have district information.')} ({data.missing_district_count})</p>}
    {!data.districts.length ? <p className="officer-notice">{text('No district location data is available yet.')}</p> : <>
      <GeographyChart title="Entrepreneurs by District" axis="District" rows={data.districts.map(row => ({ ...row, name: row.district, key: row.district_key }))} onSelect={key => navigate(entrepreneursPath(data.state_key, key))} />
      <p>{text('Share is based on profiles with a provided location.')}</p>
      <div className="officer-scroll" tabIndex={0} role="region" aria-label={text('Entrepreneurs by District')}><table className="officer-table"><caption>{text('Entrepreneurs by District')}</caption><thead><tr>{['District','Entrepreneurs','Share','New Enterprises','Existing Enterprises','Action'].map(label => <th scope="col" key={label}>{text(label)}</th>)}</tr></thead><tbody>{data.districts.map(row => <tr key={row.district_key}><th scope="row">{row.district}</th><td>{row.entrepreneur_count}</td><td>{row.percentage}%</td><td>{row.new_enterprises}</td><td>{row.existing_enterprises}</td><td><Link to={entrepreneursPath(data.state_key, row.district_key)} aria-label={`${text('View Entrepreneurs')}: ${row.district}`}>{text('View Entrepreneurs')}</Link></td></tr>)}</tbody></table></div>
    </>}
  </>
}
export function StateAnalyticsPage() {
  const { stateKey = '' } = useParams()
  const { text } = useUi()
  const { state, retry } = useAdminData<DistrictAnalytics>(`analytics/states/${encodeURIComponent(stateKey)}/districts`)
  return <section><Link to="/admin/analytics/geography">{text('Geographic Analytics')}</Link><AdminDataFeedback state={state} retry={retry} error="Unable to load district data." />{state.status === 'ready' && <DistrictAnalyticsView data={state.data} />}</section>
}
