import { useUi as useTextUi } from '../../i18n/uiContextValue'
import { LocalizedText, LocalizedDate } from '../../i18n/LocalizedText'
import { useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { businessAnalysisService } from '../../services/businessAnalysisService'
import { financialService } from '../../services/financialService'
import { profileService } from '../../services/profileService'
import { businessService } from '../../services/businessService'
import { getApiErrorMessage } from '../../services/apiError'
import { Button } from '../../components/ui/Button'
import { EvidenceMap } from '../marketAnalysis/MarketMap'
import { nearbyMapPoints } from '../marketAnalysis/evidenceMapModel'
import type { BusinessAnalysis } from '../../types/businessAnalysis'
import type { FinancialAnalysis } from '../../types/financial'
const readable = (s: string) => s.replaceAll('_', ' ')

function EvidenceLinks({ ids }: { ids: string[] }) {
  return <p className="analysis-evidence-links"><LocalizedText value={"Evidence: "} />{ids.map(id => <a key={id} href={`#evidence-${id}`}>{id} </a>)}</p>
}

export function BusinessAnalysisPage() {
  const [params] = useSearchParams()
  return <BusinessAnalysisWorkspace key={params.toString()} />
}

function BusinessAnalysisWorkspace() {
  const [params, setParams] = useSearchParams()
  const [financial, setFinancial] = useState<FinancialAnalysis | null>(null)
  const [radius, setRadius] = useState(5)
  const [result, setResult] = useState<BusinessAnalysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')
  const [reload, setReload] = useState(0)
  const request = useRef<AbortController | null>(null)
  const sourceId = params.get('financial_analysis_id')
  const resultId = params.get('analysis_id')
  useEffect(() => {
    let active = true
    const controller = new AbortController()
    const load = async () => {
      try {
        if (resultId) {
          const saved = await businessAnalysisService.get(resultId, controller.signal)
          if (active) { setResult(saved); setRadius(saved.market_context.radius.selected_km) }
          const source = await financialService.get(saved.financial_context.analysis.id)
          if (active) setFinancial(source)
        } else if (sourceId) {
          const source = await financialService.get(sourceId)
          if (active) setFinancial(source)
        } else {
          const [profile, catalog] = await Promise.all([profileService.get(), businessService.list()])
          const proposed = catalog.find(b => b.id === profile?.proposedBusinessId)
          if (!proposed) throw new Error('Choose an active proposed business in Profile first.')
          const source = await financialService.latest(proposed.slug)
          if (active) setFinancial(source)
        }
      } catch (reason) { if (active) setError(reason instanceof Error && !('response' in reason) ? reason.message : getApiErrorMessage(reason, 'Unable to load analysis context.')) }
      finally { if (active) setLoading(false) }
    }
    void load()
    return () => { active = false; controller.abort(); request.current?.abort() }
  }, [sourceId, resultId, reload])
  const run = async () => {
    if (!financial) return
    request.current?.abort()
    const controller = new AbortController()
    request.current = controller
    setRunning(true); setError(''); setResult(null)
    try {
      const response = await businessAnalysisService.analyze(financial.id, radius, controller.signal)
      if (!controller.signal.aborted) { setResult(response); setParams({ analysis_id: response.id }, { replace: true }) }
    } catch (reason) { if (!controller.signal.aborted) setError(getApiErrorMessage(reason, 'Unable to generate business analysis.')) }
    finally { if (!controller.signal.aborted) setRunning(false) }
  }
  return <div className="workspace-page business-analysis-page">
    <header><h1><LocalizedText value={"Business Analysis"} /></h1><p><LocalizedText value={"Evidence-based SWOT, threats, competitor mapping and indicative pricing guidance."} /></p></header>
    <nav><Link to="/profile"><LocalizedText value={"Review Profile"} /></Link> · <Link to="/financial-plan"><LocalizedText value={"Financial Plan"} /></Link> · <Link to="/market-analysis"><LocalizedText value={"Market Analysis"} /></Link></nav>
    {loading ? <p role="status"><LocalizedText value={"Loading saved financial context…"} /></p> : <section className="profile-card">
      <h2><LocalizedText value={"Business Overview"} /></h2>
      {financial ? <><h3>{financial.business.name}</h3><p><LocalizedText value={"Saved margin: ₹"} />{financial.availableMarginCapital}<LocalizedText value={" · Project capacity: ₹"} />{financial.feasibleProjectCost}</p>
        <label><LocalizedText value={"Market radius "} /><select value={radius} disabled={running} onChange={e => { setRadius(Number(e.target.value)); setResult(null) }}>{Array.from({ length: 10 }, (_, i) => i + 1).map(r => <option key={r} value={r}>{r}<LocalizedText value={" km"} /></option>)}</select></label>
        <Button disabled={running} onClick={() => void run()}><LocalizedText value={running ? 'Analysing evidence…' : 'Generate Business Analysis'} /></Button>
      </> : <p><LocalizedText value={"Save a financial plan for your proposed business first."} /></p>}
    </section>}
    {error && <div className="profile-error" role="alert"><LocalizedText value={error} /> <Button onClick={() => { setError(''); setLoading(true); setReload(n => n + 1) }}><LocalizedText value={"Reload context"} /></Button></div>}
    {running && <p role="status"><LocalizedText value={"Resolving current market evidence and evaluating planning rules…"} /></p>}
    {result && <AnalysisResults result={result} />}
  </div>
}

function AnalysisResults({ result }: { result: BusinessAnalysis }) {
  const { text: textUi } = useTextUi()

  const market = result.market_context
  const competition = result.competition
  const source = market.source.cache_status === 'STALE_CACHE' ? 'STALE CACHE' : market.source.mode
  return <div className="analysis-sections">
    <p><LocalizedText value={"Saved "} /><LocalizedDate value={result.created_at} /><LocalizedText value={" · Snapshot "} />{result.id}<LocalizedText value={". Saved results retain their original evidence."} /></p>
    <section><h2><LocalizedText value={"SWOT Analysis"} /></h2><div className="analysis-quadrants">{Object.entries(result.swot).map(([quadrant, items]) => <article className="profile-card" key={quadrant}><h3><LocalizedText value={quadrant} /></h3>{items.length ? items.map(item => <div key={item.id}><h4><LocalizedText value={item.title} /></h4><p><LocalizedText value={item.explanation} /></p>{item.importance && <small><LocalizedText value={item.importance} /><LocalizedText value={" importance"} /></small>}<EvidenceLinks ids={item.evidence_ids} />{item.finding_ids.map(id => <a key={id} href={`#${id}`}><LocalizedText value={"View threat finding "} /></a>)}</div>) : <p><LocalizedText value={"No supported finding for this quadrant."} /></p>}</article>)}</div></section>
    <section><h2><LocalizedText value={"Local Threats"} /></h2><div className="analysis-quadrants">{result.local_threats.map(t => <article className="profile-card" key={t.id} id={t.id}><h3><LocalizedText value={t.title} /></h3><p><LocalizedText value={readable(t.evidence_kind)} /><LocalizedText value={" · Severity: "} /><LocalizedText value={t.severity ?? 'Unclassified'} /><LocalizedText value={" · Likelihood: "} /><LocalizedText value={t.likelihood ?? 'Not established'} /></p><p><LocalizedText value={t.description} /></p>{t.severity_reason && <p><LocalizedText value={t.severity_reason} /></p>}<strong><LocalizedText value={"Mitigation"} /></strong><p><LocalizedText value={t.mitigation} /></p>{t.coverage_warnings.map(w => <p key={w}><LocalizedText value={w} /></p>)}<EvidenceLinks ids={t.evidence_ids} /></article>)}</div></section>
    <section className="profile-card"><h2><LocalizedText value={"Competitor Mapping"} /></h2><p><LocalizedText value={source} /><LocalizedText value={" · Evidence fetched "} /><LocalizedDate value={market.source.fetched_at} /></p>
      <dl className="scheme-panel__metrics"><div><dt><LocalizedText value={"Radius"} /></dt><dd>{competition.selected_radius_km}<LocalizedText value={" km"} /></dd></div><div><dt><LocalizedText value={"Direct mapped competitors"} /></dt><dd>{competition.direct_count ?? <LocalizedText value="Unavailable" />}</dd></div><div><dt><LocalizedText value={"Related businesses"} /></dt><dd>{competition.related_count ?? <LocalizedText value="Unavailable" />}</dd></div><div><dt><LocalizedText value={"Nearest direct competitor"} /></dt><dd>{competition.nearest ? <>{competition.nearest.name} · {competition.nearest.distance_km}<LocalizedText value=" km" /></> : <LocalizedText value="No mapped direct evidence" />}</dd></div><div><dt><LocalizedText value={"Average direct distance"} /></dt><dd><LocalizedText value={competition.average_distance == null ? 'Unavailable' : `${(competition.average_distance / 1000).toFixed(2)} km`} /></dd></div><div><dt><LocalizedText value={"Mapped direct competitors per km²"} /></dt><dd>{competition.mapped_density?.toFixed(4) ?? <LocalizedText value="Unavailable" />}</dd></div></dl>
      <h3><LocalizedText value={readable(competition.classification)} /></h3><p><LocalizedText value={"Provisional planning classification; not a calibrated market score."} /></p><p><LocalizedText value={competition.classification_basis} /></p><h3><LocalizedText value={"Distance concentration bands"} /></h3><ul>{competition.distance_bands.map(b => <li key={b.lower_km}><LocalizedText value={b.lower_km === 0 ? '0' : `>${b.lower_km}`} />–{b.upper_km}<LocalizedText value={" km: "} />{b.count}</li>)}</ul><EvidenceLinks ids={competition.evidence_ids} />
      <EvidenceMap latitude={market.location.latitude} longitude={market.location.longitude} title={textUi("Mapped competitor evidence")} centreName={textUi(market.location.display_name)} evidenceProvider={market.source.provider} radiusMeters={market.radius.selected_meters} textLabel={textUi("Accessible mapped business list")} points={nearbyMapPoints([...market.competitors, ...market.related_businesses])} />
    </section>
    <section className="profile-card"><h2><LocalizedText value={"Pricing & Product Market Value"} /></h2><p><LocalizedText value={readable(result.pricing.status)} /></p><p><LocalizedText value={result.pricing.strategy} /></p>{result.pricing.items.map(item => <article key={`${item.name}-${item.unit}`}><h3>{item.name} / {item.unit}</h3><p><LocalizedText value={"Indicative range ₹"} />{item.recommended_min}–₹{item.recommended_max}<LocalizedText value={"; target ₹"} />{item.recommended_target}<LocalizedText value={"; planning cost ₹"} />{item.planning_cost_per_unit}</p></article>)}{result.pricing.assumptions.length > 0 && <details><summary><LocalizedText value={"Available planning assumptions"} /></summary><pre>{JSON.stringify(result.pricing.assumptions, null, 2)}</pre></details>}<h3><LocalizedText value={"Missing assumptions"} /></h3><ul>{result.pricing.missing_assumptions.map(a => <li key={a}><LocalizedText value={a} /></li>)}</ul><p><LocalizedText value={readable(result.pricing.demographic_status)} /></p><p><LocalizedText value={readable(result.pricing.purchasing_power_status)} /> · <LocalizedText value={readable(result.pricing.local_price_status)} /></p>{result.pricing.warnings.map(w => <p key={w}><LocalizedText value={w} /></p>)}<EvidenceLinks ids={result.pricing.evidence_ids} /></section>
    <section className="profile-card"><h2><LocalizedText value={"Evidence & Data Quality"} /></h2><p><LocalizedText value={source} /> · {market.quality.attribution}</p>{market.quality.warnings.map(w => <p key={w.code}><LocalizedText value={w.message} /></p>)}{Object.entries(result.quality.warnings).map(([kind, values]) => values.length > 0 && <p key={kind}><LocalizedText value={kind} />: {values.map((value, index) => <span key={index}>{index > 0 && ", "}<LocalizedText value={value} /></span>)}</p>)}<details><summary><LocalizedText value={"Rule versions"} /></summary><pre>{JSON.stringify(result.quality.rule_versions, null, 2)}</pre><p><LocalizedText value={"Context hash: "} />{result.quality.context_hash}</p></details>{result.evidence.map(e => <details key={e.id} id={`evidence-${e.id}`}><summary>{e.id} · <LocalizedText value={readable(e.source_kind)} /></summary><p><LocalizedText value={"Source: "} />{e.source_ref} {e.observed_at && <>· <LocalizedDate value={e.observed_at} /></>}</p><pre>{JSON.stringify(e.value, null, 2)}</pre>{e.limitations.map(l => <p key={l}><LocalizedText value={l} /></p>)}</details>)}</section>
  </div>
}
