import { useAdminData } from './useAdminData'
import { entrepreneurQuery, filtersQuery, pageQuery } from './entrepreneurFilters'
import type { FormEvent } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useUi } from '../../i18n/uiContextValue'
import type { EntrepreneurPage } from '../../services/adminService'
import { AdminDataFeedback } from './AdminData'

export function EntrepreneurFilters({ params, apply, clear }: { params: URLSearchParams; apply: (params: URLSearchParams) => void; clear: () => void }) {
  const { text } = useUi()
  const submit = (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); apply(filtersQuery(new FormData(event.currentTarget))) }
  return <form className="officer-filters" onSubmit={submit} key={params.toString()}><fieldset><legend>{text('Filters')}</legend>
    <label>{text('Search')}<input name="search" maxLength={160} defaultValue={params.get('search') ?? ''} placeholder={text('Name, email, mobile or location')} /></label>
    <label>{text('State')}<input name="state" maxLength={100} defaultValue={params.get('state') ?? ''} /></label>
    <label>{text('District')}<input name="district" maxLength={100} defaultValue={params.get('district') ?? ''} /></label>
    <label>{text('Enterprise Type')}<select name="enterprise_status" defaultValue={params.get('enterprise_status') ?? ''}>{[['','All'],['new','New'],['existing','Existing'],['unspecified','Not Specified']].map(([value,label]) => <option key={value} value={value}>{text(label)}</option>)}</select></label>
    <label>{text('Sort')}<select name="sort" defaultValue={params.get('sort') ?? 'created_desc'}><option value="created_desc">{text('Newest Registered')}</option><option value="created_asc">{text('Oldest Registered')}</option></select></label>
    <label>{text('Rows per page')}<select name="page_size" defaultValue={params.get('page_size') ?? '20'}>{[20,50,100].map(size => <option key={size} value={size}>{size}</option>)}</select></label>
    <div className="officer-filter-actions"><button type="submit">{text('Apply Filters')}</button><button type="button" onClick={clear}>{text('Clear Filters')}</button></div>
  </fieldset></form>
}
export function EntrepreneurListView({ data, onPage }: { data: EntrepreneurPage; onPage: (page: number) => void }) {
  const { text, date } = useUi()
  const show = (value: string | null) => value?.trim() || text('Not Provided')
  return <><p>{text('Matching user accounts')}: {data.total}</p>{data.items.length === 0 ? <p className="officer-notice">{text('No entrepreneurs match these filters.')}</p> :
    <div className="officer-scroll" tabIndex={0} role="region" aria-label={text('Entrepreneurs')}><table className="officer-table officer-entrepreneurs"><caption>{text('Entrepreneurs')}</caption><thead><tr>{['Entrepreneur','Email','Mobile','State','District','Taluka / Block','Village','Enterprise Type','Proposed Business','Preferred Language','Registered Date','Profile Status'].map(label => <th key={label} scope="col">{text(label)}</th>)}</tr></thead><tbody>{data.items.map(row => <tr key={row.email}>
      <th scope="row">{row.full_name}</th><td>{row.email}</td><td>{row.mobile_number}</td><td>{show(row.state)}</td><td>{show(row.district)}</td><td>{show(row.taluka)}</td><td>{show(row.village)}</td>
      <td>{text({new:'New',existing:'Existing',unspecified:'Not Specified'}[row.enterprise_status])}</td><td>{show(row.proposed_business)}</td><td>{text(({en:'English',hi:'Hindi',mr:'Marathi'} as Record<string,string>)[row.preferred_language] ?? row.preferred_language)}</td><td>{date(row.created_at)}</td><td>{text({complete:'Complete',created:'Profile Created',pending:'Pending'}[row.profile_status])}</td>
    </tr>)}</tbody></table></div>}
    <nav className="officer-pagination" aria-label={text('Pagination')}><button disabled={data.page <= 1} onClick={() => onPage(data.page - 1)}>{text('Previous')}</button><span>{text('Page {0} of {1}').replace('{0}', String(data.page)).replace('{1}', String(Math.max(1, data.total_pages)))}</span><button disabled={data.page >= data.total_pages} onClick={() => onPage(data.page + 1)}>{text('Next')}</button></nav>
  </>
}
export function EntrepreneursPage() {
  const [params, setParams] = useSearchParams()
  const query = entrepreneurQuery(params)
  const { text } = useUi()
  const { state, retry } = useAdminData<EntrepreneurPage>(`entrepreneurs?${query}`)
  return <section><h1>{text('Entrepreneurs')}</h1><p>{text('User accounts and entrepreneur profiles. Administrator accounts are excluded.')}</p>
    <EntrepreneurFilters params={params} apply={setParams} clear={() => setParams({})} />
    {(params.get('state') || params.get('district')) && <p className="officer-notice">{text('State')}: {params.get('state') || text('All')} · {text('District')}: {params.get('district') || text('All')}</p>}
    <AdminDataFeedback state={state} retry={retry} error="Unable to load entrepreneurs." />{state.status === 'ready' && <EntrepreneurListView data={state.data} onPage={page => setParams(pageQuery(params, page))} />}
  </section>
}
