import { disclaimer, statusLabels } from './catalogLabels'
import { useCallback, useEffect, useState, useMemo } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useAuth } from '../../context/authContextValue'
import { useUi } from '../../i18n/uiContextValue'
import { governmentSchemeService } from '../../services/governmentSchemeService'
import { GovernmentSchemesPage } from '../schemes/GovernmentSchemesPage'
import { CatalogError, CatalogSkeleton, SchemeCard } from './CatalogViews'
import { debounceCatalogSearch, readCatalogQuery, sorts, updateCatalogQuery } from './catalogState'
import { useCatalogRequest } from './useCatalogRequest'

export function GovernmentSchemeCatalogPage() {
  const { text } = useUi()
  const { isAuthenticated, user } = useAuth()
  return <div className="gc-page"><header className="gc-heading"><span className="eyebrow">{text('Government Schemes')}</span><h1>{text('Government Schemes')}</h1><p>{text('Discover government schemes and financing support')}</p></header>
    <section className="gc-pathway" aria-labelledby="financing-pathway"><h2 id="financing-pathway">{text('Your Financing Pathway')}</h2><p>{text('Based on your saved financial context')}</p>
      {isAuthenticated && user?.role === 'USER' ? <GovernmentSchemesPage /> : <Link className="button button--outline" to="/login">{text('Sign in to view your financing pathway')}</Link>}
    </section><GovernmentSchemeCatalog /></div>
}

export function GovernmentSchemeCatalog() {
  const { text } = useUi()
  const [params, setParams] = useSearchParams()
  const raw = params.toString()
  const query = useMemo(() => readCatalogQuery(new URLSearchParams(raw)), [raw])
  const requestKey = JSON.stringify(query)
  const [clearVersion, setClearVersion] = useState(0)
  const loadList = useCallback((signal: AbortSignal) => governmentSchemeService.list(query, signal), [query])
  const list = useCatalogRequest(requestKey, loadList)
  const metadata = useCatalogRequest('filters', governmentSchemeService.filters)
  const change = (key: string, value: string) => setParams(updateCatalogQuery(params, key, value))
  const sortLabels = { name_asc: 'Name A–Z', name_desc: 'Name Z–A', newest: 'Newest', oldest: 'Oldest' }
  return <section className="gc-explore" aria-labelledby="catalog-title"><header><h2 id="catalog-title">{text('Explore Government Schemes')}</h2><p>{text('Browse imported Central and State government scheme information')}</p></header>
    <p className="gc-disclaimer">{text(disclaimer)}</p>
    <CatalogSearch key={`${raw}:${clearVersion}`} raw={raw} value={query.search || ''} />
    {metadata.loading ? <CatalogSkeleton label="Loading catalog filters" /> : metadata.error ? <CatalogError label="Unable to load catalog filters." retry={metadata.retry} /> : metadata.data && <div className="gc-filters">
      <label>{text('Scheme Level')}<select aria-label={text('Scheme Level')} value={query.level || ''} onChange={e => change('level', e.target.value)}><option value="">{text('All')}</option>{metadata.data.levels.map(v => <option key={v} value={v}>{text(v === 'CENTRAL' ? 'Central' : 'State')}</option>)}</select></label>
      <label>{text('State')}<select aria-label={text('State')} disabled={query.level === 'CENTRAL'} value={query.state || ''} onChange={e => change('state', e.target.value)}><option value="">{text('All States')}</option>{metadata.data.states.map(v => <option key={v}>{v}</option>)}</select></label>
      <label>{text('Category')}<select aria-label={text('Category')} value={query.category || ''} onChange={e => change('category', e.target.value)}><option value="">{text('All Categories')}</option>{metadata.data.categories.map(v => <option key={v}>{v}</option>)}</select></label>
      <label>{text('Verification Status')}<select aria-label={text('Verification Status')} value={query.verification_status || ''} onChange={e => change('verification_status', e.target.value)}><option value="">{text('All')}</option>{metadata.data.verification_statuses.map(v => <option key={v} value={v}>{text(statusLabels[v])}</option>)}</select></label>
    </div>}
    <div className="gc-toolbar"><label>{text('Sort')}<select aria-label={text('Sort')} value={query.sort} onChange={e => change('sort', e.target.value)}>{sorts.map(v => <option key={v} value={v}>{text(sortLabels[v])}</option>)}</select></label><button className="button button--outline" onClick={() => { setClearVersion(v => v + 1); setParams({}) }}>{text('Clear filters')}</button></div>
    {query.search && <p>{text('Search relevance comes before your selected sort.')}</p>}
    {list.loading ? <CatalogSkeleton label="Loading government schemes" /> : list.error ? <CatalogError label="Unable to load government schemes." retry={list.retry} /> : list.data && <>
      <p role="status">{text(`Showing ${list.data.items.length ? (list.data.page - 1) * list.data.page_size + 1 : 0}–${list.data.items.length ? (list.data.page - 1) * list.data.page_size + list.data.items.length : 0} of ${list.data.total} schemes`)}</p>
      {list.data.items.length ? <div className="gc-grid">{list.data.items.map(scheme => <SchemeCard key={scheme.slug} scheme={scheme} query={raw} />)}</div> : <div className="gc-state"><h3>{text('No schemes match your filters.')}</h3><p>{text('Try changing your search or filters.')}</p></div>}
      <nav className="gc-pagination" aria-label={text('Scheme pagination')}><button className="button button--outline" disabled={query.page <= 1} onClick={() => change('page', String(query.page - 1))}>{text('Previous')}</button><span>{text(`Page ${query.page} of ${Math.max(1, list.data.total_pages)}`)}</span><button className="button button--outline" disabled={query.page >= list.data.total_pages} onClick={() => change('page', String(query.page + 1))}>{text('Next')}</button></nav>
    </>}
  </section>
}


function CatalogSearch({ raw, value }: { raw: string; value: string }) {
  const { text } = useUi()
  const [, setParams] = useSearchParams()
  const [search, setSearch] = useState(value)
  useEffect(() => {
    if (search.trim() === value) return
    return debounceCatalogSearch(() => setParams(updateCatalogQuery(new URLSearchParams(raw), 'search', search.trim())))
  }, [raw, value, search, setParams])
  return <label className="gc-search"><span>{text('Search government schemes')}</span><input type="search" maxLength={200} value={search} placeholder={text('Search government schemes')} onChange={event => setSearch(event.target.value)} /></label>
}
