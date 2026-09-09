import { useUi as useTextUi } from '../../i18n/uiContextValue'
import { LocalizedText, LocalizedDate } from '../../i18n/LocalizedText'
import { useEffect, useReducer, useRef, useState } from 'react'
import { NearbySearchControls } from './NearbySearchControls'
import { Button } from '../../components/ui/Button'
import { Alert } from '../../components/ui/Feedback'
import { useUi } from '../../i18n/uiContextValue'
import { businessService } from '../../services/businessService'
import { profileService } from '../../services/profileService'
import { marketService } from '../../services/marketService'
import { getApiErrorMessage } from '../../services/apiError'
import type { BusinessListItem } from '../../types/business'
import type { NearbyMarketEvidence, NearbyPOI } from '../../types/nearbyMarket'
import { initialNearbyState, nearbyReducer, normalizeBusinessQuery, validBusinessQuery } from './nearbyState'
import { EvidenceMap } from './MarketMap'
import { nearbyMapPoints } from './evidenceMapModel'

function profileKey(profile: Awaited<ReturnType<typeof profileService.get>>) {
  return JSON.stringify([profile?.village, profile?.taluka, profile?.district, profile?.state, profile?.pincode])
}

export function NearbyBusinessEvidence() {
  const { text: textUi } = useTextUi()

  const { t } = useUi()
  const labels = t.nearbyMarket
  const [businesses, setBusinesses] = useState<BusinessListItem[]>([])
  const [{ query, radius, result }, dispatch] = useReducer(nearbyReducer, initialNearbyState)
  const setResult = (value: NearbyMarketEvidence | null) => dispatch({ type: 'result', value })
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')
  const [queryTouched, setQueryTouched] = useState(false)
  const queryInvalid = queryTouched && !validBusinessQuery(query)
  const request = useRef<AbortController | null>(null)
  const fingerprint = useRef('')

  useEffect(() => {
    let active = true
    void businessService.list().then(items => { if (active) setBusinesses(items) }).catch(() => { /* Suggestions are optional. */ })
    return () => { active = false; request.current?.abort() }
  }, [])

  useEffect(() => {
    let active = true
    const refreshProfile = async () => {
      try {
        const profile = await profileService.get()
        if (!active) return
        const next = profileKey(profile)
        if (fingerprint.current && next !== fingerprint.current) {
          request.current?.abort(); setResult(null); setRunning(false)
        }
        fingerprint.current = next
      } catch { /* Keep the displayed snapshot until a location change is confirmed. */ }
    }
    window.addEventListener('focus', refreshProfile)
    return () => { active = false; window.removeEventListener('focus', refreshProfile) }
  }, [])

  const run = async () => {
    if (!validBusinessQuery(query)) { setError('Enter a business idea with 2–200 characters.'); return }
    const submittedQuery = normalizeBusinessQuery(query)
    request.current?.abort()
    const controller = new AbortController()
    request.current = controller
    setError(''); setRunning(true)
    try {
      const before = await profileService.get()
      fingerprint.current = profileKey(before)
      if (controller.signal.aborted) return
      const response = await marketService.nearby(submittedQuery, radius, controller.signal)
      const after = await profileService.get()
      if (controller.signal.aborted || request.current !== controller) return
      if (profileKey(after) !== profileKey(before)) { setError(labels.changed); return }
      if (response.business_query !== submittedQuery || response.radius.selected_km !== radius) { setError(labels.changed); return }
      setResult(response)
    } catch (reason) {
      if (!controller.signal.aborted && request.current === controller) setError(getApiErrorMessage(reason, 'Unable to load nearby business evidence.'))
    } finally {
      if (!controller.signal.aborted && request.current === controller) setRunning(false)
    }
  }

  return <section className="market-page nearby-evidence">
    <header className="market-heading"><h1><LocalizedText value={labels.title} /></h1><p><LocalizedText value={"Nearby business evidence is provider-dependent and is not a complete establishment census."} /></p></header>
    <NearbySearchControls query={query} radius={radius} queryInvalid={queryInvalid} running={running}
      businesses={businesses} labels={labels} textUi={textUi} onQueryBlur={() => setQueryTouched(true)}
      onQueryChange={value => {
        request.current?.abort(); setRunning(false); setError(''); dispatch({ type: 'query', value })
      }}
      onRadiusChange={value => {
        request.current?.abort(); setRunning(false); setError(''); dispatch({ type: 'radius', value })
      }}
      onRun={() => void run()} />
    {running && <p role="status">{labels.loading}</p>}
    {error && <Alert tone="danger"><LocalizedText value={error} /> <Button type="button" disabled={running} onClick={() => void run()}>{labels.retry}</Button></Alert>}
    {result && <NearbyResults result={result} />}
  </section>
}

export function NearbyResults({ result }: { result: NearbyMarketEvidence }) {
  const { text: textUi } = useTextUi()

  const { t } = useUi()
  const labels = t.nearbyMarket
  const classification = (poi: NearbyPOI) => poi.classification === 'DIRECT_COMPETITOR' ? labels.direct : poi.classification === 'RELATED_BUSINESS' ? labels.related : textUi('Uncertain relevance')
  const list = (items: NearbyPOI[]) => <ul className="nearby-pois">{items.map(poi => <li key={`${poi.external_type}-${poi.external_id}`}>
    <strong>{poi.name}</strong><p>{poi.distance_km}<LocalizedText value={" km · "} />{classification(poi)}</p>
    {poi.provider === 'GOOGLE_PLACES' ? <>
      <p>{labels.source}: Google Places</p>
      {poi.normalized_address.formatted_address && <p>{poi.normalized_address.formatted_address}</p>}
      <a href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(poi.name)}&query_place_id=${encodeURIComponent(poi.external_id)}`} target="_blank" rel="noreferrer">{textUi('View on Google Maps')}</a>
    </> : <>
      <p>{labels.source}: OpenStreetMap / Overpass</p>
      <p>{labels.evidence}: {poi.matching_evidence.map(tag => `${tag.key}=${tag.value}`).join(', ')}</p>
      <a href={`https://www.openstreetmap.org/${poi.external_type}/${encodeURIComponent(poi.external_id)}`} target="_blank" rel="noreferrer">{labels.osm}</a>
    </>}

  </li>)}</ul>
  const google = result.source.provider === 'GOOGLE_PLACES'
  const empty = google ? 'No mapped direct competitors were found in the available Google Places data.' : labels.empty
  const source = result.source.cache_status === 'STALE_CACHE' ? labels.stale : result.source.mode === 'LIVE' ? labels.live : labels.cache
  return <div className="market-results" aria-live="polite">
    <section className="market-summary"><h2>{result.business_query ?? result.business.display_name}</h2>
      {google && <><p>{textUi('Nearby businesses found through Google Places')}</p><p>{textUi('Google Places returns available/ranked search results and may not include every establishment in the selected area.')}</p></>}
      {!result.matched_catalog_business_slug && !result.business.slug && <p>{textUi('Full SWOT and pricing rules require a catalog business profile.')}</p>}
      <p>{labels.location}: {result.location.display_name}</p>
      <p>{labels.showing.replace('{radius}', String(result.radius.selected_km))}</p>
      <span className="badge badge--navy">{labels.source}: {google ? 'Google Places' : 'OpenStreetMap / Overpass'} · {source}</span>
      <p>{labels.fetched}: <LocalizedDate value={result.source.fetched_at} />{!google && <> · {labels.expires}: <LocalizedDate value={result.source.expires_at} /></>}</p>
      <dl className="scheme-panel__metrics">
        <div><dt>{labels.radius}</dt><dd>{result.radius.selected_km}<LocalizedText value={" km"} /></dd></div>
        <div><dt>{labels.direct}</dt><dd>{result.summary.direct_competitors}</dd></div>
        <div><dt>{labels.related}</dt><dd>{result.summary.related_businesses}</dd></div>
        <div><dt>{labels.nearest}</dt><dd>{result.summary.nearest_direct_competitor ? <>{result.summary.nearest_direct_competitor.name} · {result.summary.nearest_direct_competitor.distance_km}<LocalizedText value=" km" /></> : '—'}</dd></div>
      </dl>
      {result.quality.warnings.filter(warning => !(google && warning.code === 'GOOGLE_RANKED_SUBSET')).map(warning => <p className="nearby-warning" key={warning.code}><LocalizedText value={warning.code === 'NO_MAPPED_DIRECT_COMPETITORS' ? empty : warning.code === 'OSM_COVERAGE_LIMITED' ? labels.notice : warning.message} /></p>)}
      <p><LocalizedText value={"Business evidence: "} /><LocalizedText value={google ? 'Google Places' : 'OpenStreetMap / Overpass'} /> · {google ? result.quality.attribution : <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">{result.quality.attribution}</a>}</p>
    </section>
    <EvidenceMap latitude={result.location.latitude} longitude={result.location.longitude} title={textUi(labels.map)} centreName={result.location.display_name}
      evidenceProvider={result.source.provider} radiusMeters={result.radius.selected_meters} textLabel={textUi(labels.text)}
      points={nearbyMapPoints([...result.competitors, ...result.related_businesses, ...(result.generic_pois ?? [])])} />
    <section className="market-business-section"><h2>{labels.direct}</h2>{result.competitors.length ? list(result.competitors) : <p><LocalizedText value={empty} /></p>}</section>
    {!!result.generic_pois?.length && <section className="market-business-section"><h2>{textUi('Uncertain relevance')}</h2>{list(result.generic_pois)}</section>}
    <section className="market-business-section"><h2>{labels.related}</h2>{result.related_businesses.length ? list(result.related_businesses) : <p>{labels.noRelated}</p>}</section>
  </div>
}
