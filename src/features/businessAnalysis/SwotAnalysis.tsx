import { AlertCircle, Lightbulb, ShieldAlert, ShieldCheck } from 'lucide-react'
import { useUi } from '../../i18n/uiContextValue'
import { LocalizedDate } from '../../i18n/LocalizedText'
import type { AnalysisFinding, BusinessAnalysis } from '../../types/businessAnalysis'
import { findingSources, sourceLabels } from './swotPresentation'
import './swot.css'

const quadrants = [
  { key: 'strengths', label: 'Strengths', subtitle: 'Capabilities and common business advantages', Icon: ShieldCheck },
  { key: 'weaknesses', label: 'Weaknesses', subtitle: 'Internal constraints to plan for', Icon: AlertCircle },
  { key: 'opportunities', label: 'Opportunities', subtitle: 'Possibilities to investigate and validate', Icon: Lightbulb },
  { key: 'threats', label: 'Threats', subtitle: 'Risks to anticipate and manage', Icon: ShieldAlert },
] as const

export function SwotAnalysis({ result }: { result: Pick<BusinessAnalysis, 'swot' | 'evidence'> }) {
  const { text } = useUi()
  return <section className="swot-report" aria-labelledby="swot-heading"><h2 id="swot-heading">{text('SWOT Analysis')}</h2>
    <p className="swot-disclosure">{text('Baseline findings describe common business characteristics. Local findings are shown separately when supported by profile or market evidence.')}</p>
    <div className="swot-grid">{quadrants.map(({ key, label, subtitle, Icon }) => {
      const items = result.swot[key] ?? []
      return <article className={`swot-quadrant swot-quadrant--${key}`} key={key} aria-labelledby={`swot-${key}`}>
        <header className="swot-quadrant-header"><Icon aria-hidden="true" /><div><h3 id={`swot-${key}`}>{text(label)}</h3><p>{text(subtitle)}</p></div><span className="swot-count" aria-label={`${text('SWOT Findings')}: ${items.length}`}>{items.length}</span></header>
        {items.length ? <ul className="swot-findings">{items.map(item => <SwotFinding key={item.id} item={item} evidence={result.evidence} conciseThreat={key === 'threats'} />)}</ul> : <p className="swot-empty">{text('No supported finding for this quadrant.')}</p>}
      </article>
    })}</div>
  </section>
}

function SwotFinding({ item, evidence, conciseThreat }: { item: AnalysisFinding; evidence: BusinessAnalysis['evidence']; conciseThreat: boolean }) {
  const { text } = useUi()
  const sources = findingSources(item)
  const baseline = sources.includes('BUSINESS_BASELINE')
  const technical = item.evidence_ids.map(id => evidence.find(value => value.id === id)).filter(value => value !== undefined)
  const detailedThreat = conciseThreat && !baseline && item.finding_ids.length > 0
  const priority = item.importance === 'HIGH' ? 'High priority' : item.importance === 'MEDIUM' ? 'Medium priority' : 'Advisory'
  return <li className="swot-finding">
    <h4 lang={baseline ? 'en' : undefined}>{baseline ? item.title : text(item.title)}</h4>
    {!detailedThreat && <p lang={baseline ? 'en' : undefined}>{baseline ? item.explanation : text(item.explanation)}</p>}
    {detailedThreat && <a className="swot-risk-link" href={`#${item.finding_ids[0]}`}>{text('Read the detailed risk assessment')}</a>}
    <div className="swot-badges">{sources.map(source => <span className={`swot-source${source === 'BUSINESS_BASELINE' ? ' swot-source--baseline' : ''}`} key={source}>{text(sourceLabels[source])}</span>)}
      {item.importance && <span className={`swot-priority swot-priority--${item.importance.toLowerCase()}`}>{text(priority)}</span>}
    </div>
    <details className="swot-evidence"><summary>{text('Evidence details')}</summary>
      {detailedThreat && <p>{text(item.explanation)}</p>}
      <ul>{item.evidence_ids.map(id => <li key={id}><a href={`#evidence-${id}`}>{id}</a></li>)}</ul>
      {technical.map(value => <p key={value.id}>{text('Source')}: {value.source_ref}{value.radius_km != null && <> · {value.radius_km} {text('km')}</>}</p>)}
      {item.limitations.map(value => <p key={value}>{text(value)}</p>)}
    </details>
  </li>
}

export function AnalysisSummary({ result }: { result: BusinessAnalysis }) {
  const { text } = useUi()
  const findings = Object.values(result.swot).flat()
  const sources = [...new Set(findings.flatMap(findingSources))]
  return <><div className="analysis-saved"><span>{text('Analysis saved')} · <LocalizedDate value={result.created_at} /></span><details><summary>{text('View analysis details')}</summary><p>{text('Snapshot')}: {result.id}</p><p>{text('Saved results retain their original evidence.')}</p></details></div>
    <dl className="swot-summary"><div><dt>{text('Business')}</dt><dd>{result.business.name}</dd></div><div><dt>{text('Market Radius')}</dt><dd>{result.market_context.radius.selected_km} {text('km')}</dd></div><div><dt>{text('SWOT Findings')}</dt><dd>{findings.length}</dd></div><div><dt>{text('Evidence Sources')}</dt><dd>{sources.length ? sources.map(source => text(sourceLabels[source])).join(' · ') : text('Not Provided')}</dd></div></dl>
  </>
}
