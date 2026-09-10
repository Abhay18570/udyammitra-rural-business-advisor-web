import { disclaimer, statusLabels } from './catalogLabels'
import { Link } from 'react-router-dom'
import { useUi } from '../../i18n/uiContextValue'
import type { GovernmentSchemeDetail, GovernmentSchemeListItem } from '../../types/governmentScheme'
export function Provenance({ scheme }: { scheme: Pick<GovernmentSchemeListItem, 'verification_status' | 'source_type'> }) {
  const { text } = useUi()
  return <div className="gc-badges"><span className={`gc-badge gc-status--${scheme.verification_status}`}>{text(statusLabels[scheme.verification_status])}</span><span className="gc-badge">{scheme.source_type === 'DATASET' ? text('Dataset') : scheme.source_type}</span></div>
}
export function CatalogSkeleton({ label }: { label: string }) {
  const { text } = useUi()
  return <div role="status" aria-label={text(label)} className="gc-skeleton"><span className="sr-only">{text(label)}</span>{[0,1,2].map(i => <div key={i} aria-hidden="true"><i /><i /><i /></div>)}</div>
}
export function CatalogError({ label, retry }: { label: string; retry: () => void }) {
  const { text } = useUi()
  return <div role="alert" className="gc-state"><p>{text(label)}</p><button className="button button--outline" onClick={retry}>{text('Retry')}</button></div>
}
export function SchemeCard({ scheme, query }: { scheme: GovernmentSchemeListItem; query: string }) {
  const { text } = useUi()
  return <article className="gc-card"><div className="gc-badges"><span className="gc-badge">{text(scheme.level === 'CENTRAL' ? 'Central' : 'State')}</span>{scheme.level === 'STATE' && scheme.state && <span>{scheme.state}</span>}</div>
    <h3>{scheme.scheme_name}</h3><div className="gc-badges">{scheme.categories.slice(0,2).map(c => <span className="gc-category" key={c}>{c}</span>)}{scheme.categories.length > 2 && <span>{text(`+${scheme.categories.length - 2} more`)}</span>}</div>
    <p>{scheme.short_description}</p><Provenance scheme={scheme} />
    <Link className="button button--outline" to={`/government-schemes/${encodeURIComponent(scheme.slug)}${query ? `?${query}` : ''}`} aria-label={`${text('View Scheme')}: ${scheme.scheme_name}`}>{text('View Scheme')}</Link>
  </article>
}
export function SchemeDetailContent({ scheme }: { scheme: GovernmentSchemeDetail }) {
  const { text } = useUi()
  const sections = [['Scheme Overview',scheme.details],['Benefits',scheme.benefits],['Eligibility',scheme.eligibility],['Application Process',scheme.application_process],['Documents Required',scheme.documents_required]]
  return <><header><h1>{scheme.scheme_name}</h1><Provenance scheme={scheme} /></header>
    <p className="gc-disclaimer">{text(scheme.verification_status === 'VERIFIED' ? 'This record is marked verified. Check current official terms before applying.' : disclaimer)}</p>
    <dl className="gc-facts"><div><dt>{text('Scheme Level')}</dt><dd>{text(scheme.level === 'CENTRAL' ? 'Central' : 'State')}</dd></div>{scheme.state && <div><dt>{text('State')}</dt><dd>{scheme.state}</dd></div>}</dl>
    {sections.map(([title, content]) => <section className="gc-detail-section" key={title}><h2>{text(title)}</h2><p className="gc-prose">{content || text('Not provided in the dataset.')}</p></section>)}
    <section className="gc-detail-section"><h2>{text('Categories')}</h2><div className="gc-badges">{scheme.categories.map(c => <span className="gc-category" key={c}>{c}</span>)}</div><h2>{text('Tags')}</h2><div className="gc-badges">{scheme.tags.map(tag => <span className="gc-category" key={tag}>{tag}</span>)}</div></section>
    <section className="gc-detail-section"><h2>{text('Source & Verification')}</h2><Provenance scheme={scheme} /><p>{text('Source dataset')}: {scheme.source_dataset}</p><p>{text('Official source link not available in this dataset.')}</p></section>
  </>
}
