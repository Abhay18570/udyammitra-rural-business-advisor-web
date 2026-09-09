import { useUi as useTextUi } from '../../i18n/uiContextValue'
import { LocalizedText } from '../../i18n/LocalizedText'
import { Component, useEffect, useId, useState, useSyncExternalStore, type ReactNode } from 'react'
import { APIProvider, APILoadingStatus, Map, AdvancedMarker, Pin, InfoWindow, useApiLoadingStatus, useMap } from '@vis.gl/react-google-maps'
import { createSearchArea } from './googleMapArea'
import type { MarketAnalysis } from '../../types/market'
import { markerRoles, validCoordinates, type EvidenceMapPoint } from './evidenceMapModel'

interface EvidenceMapProps {
  latitude: number; longitude: number; title: string; centreName: string
  radiusMeters: number; points: EvidenceMapPoint[]; textLabel: string; demonstration?: boolean; evidenceProvider?: string
}
const failureMessage = 'Google Maps could not load. Business evidence remains available below.'
function MapMessage({ children }: { children: ReactNode }) {
  return <div className="map-message" role="status">{children}</div>
}
class MapErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false }
  static getDerivedStateFromError() { return { failed: true } }
  render() { return this.state.failed ? <MapMessage><LocalizedText value={failureMessage} /></MapMessage> : this.props.children }
}

function SearchArea({ latitude, longitude, radiusMeters, points }: EvidenceMapProps) {
  const map = useMap()
  // Stable scalar signature prevents unrelated page renders from resetting the camera.
  const positions = JSON.stringify(points.filter(p => validCoordinates(p.latitude, p.longitude)).map(p => ({ lat: p.latitude, lng: p.longitude })))
  useEffect(() => {
    if (!map) return
    const { circle, bounds } = createSearchArea(map, latitude, longitude, radiusMeters, JSON.parse(positions))
    let fitted = false
    const fit = () => {
      if (fitted || !map.getDiv().clientWidth || !map.getDiv().clientHeight) return
      map.fitBounds(bounds, 32)
      fitted = true
    }
    // Also fits maps first mounted inside a closed disclosure when it opens.
    // Subsequent container resizes preserve the user's camera; Google resizes its canvas.
    const observer = new ResizeObserver(fit)
    observer.observe(map.getDiv())
    fit()
    return () => { observer.disconnect(); circle.setMap(null) }
  }, [map, latitude, longitude, radiusMeters, positions])
  return null
}

// Google's authentication callback can arrive after the script reports LOADED.
// Share one subscription across map consumers and restore any previous handler.
let authenticationFailed = false
const authListeners = new Set<() => void>()
let restoreAuth: (() => void) | undefined
function subscribeAuth(listener: () => void) {
  const target = window as Window & { gm_authFailure?: () => void }
  const previous = target.gm_authFailure
  const handler = () => {
    authenticationFailed = true
    authListeners.forEach(notify => notify())
    previous?.()
  }
  if (!authListeners.size) {
    target.gm_authFailure = handler
    restoreAuth = () => { if (target.gm_authFailure === handler) target.gm_authFailure = previous }
  }
  authListeners.add(listener)
  return () => {
    authListeners.delete(listener)
    if (!authListeners.size) { restoreAuth?.(); restoreAuth = undefined }
  }
}

function GoogleEvidenceMap(props: EvidenceMapProps) {
  const { text: textUi } = useTextUi()
  const status = useApiLoadingStatus()
  const authFailed = useSyncExternalStore(subscribeAuth, () => authenticationFailed, () => false)
  const [selected, setSelected] = useState<string | null>(null)
  const [timedOut, setTimedOut] = useState(false)
  useEffect(() => {
    if (status === APILoadingStatus.LOADED) return
    const timer = window.setTimeout(() => setTimedOut(true), 20000)
    return () => window.clearTimeout(timer)
  }, [status])
  if (authFailed || status === APILoadingStatus.FAILED || status === APILoadingStatus.AUTH_FAILURE || (timedOut && status !== APILoadingStatus.LOADED)) return <MapMessage><LocalizedText value={failureMessage} /></MapMessage>
  if (status !== APILoadingStatus.LOADED) return <MapMessage><LocalizedText value={"Loading Google Maps…"} /></MapMessage>
  const centre = { lat: props.latitude, lng: props.longitude }
  const point = props.points.find(p => p.id === selected)
  return <Map defaultCenter={centre} defaultZoom={11} mapId="DEMO_MAP_ID" gestureHandling="cooperative" disableDefaultUI={false} streetViewControl={false} mapTypeControl={false} clickableIcons={false} onClick={() => setSelected(null)}>
    <SearchArea {...props} />
    <AdvancedMarker position={centre} title={`${textUi("Analysis centre")}: ${props.centreName}`} onClick={() => setSelected('centre')} zIndex={1000}>
      <Pin background={markerRoles.CENTRE.color} borderColor="#fff" glyphColor="#fff" glyph="C" scale={1.2} />
    </AdvancedMarker>
    {props.points.filter(p => validCoordinates(p.latitude, p.longitude)).map(p => <AdvancedMarker key={p.id} position={{ lat: p.latitude, lng: p.longitude }} title={`${textUi(markerRoles[p.role].label)}: ${p.name}`} onClick={() => setSelected(p.id)}>
      <Pin background={markerRoles[p.role].color} borderColor="#fff" glyphColor="#fff" glyph={markerRoles[p.role].glyph} />
    </AdvancedMarker>)}
    {selected === 'centre' && <InfoWindow position={centre} onCloseClick={() => setSelected(null)}><strong><LocalizedText value={"Analysis centre"} /></strong><p>{props.centreName}</p></InfoWindow>}
    {point && <InfoWindow position={{ lat: point.latitude, lng: point.longitude }} onCloseClick={() => setSelected(null)}><div className="map-info"><strong>{point.name}</strong><p><LocalizedText value={markerRoles[point.role].label} /></p><p><LocalizedText value={point.detail} /></p><p><LocalizedText value={"Evidence source: "} /><LocalizedText value={point.source} /></p></div></InfoWindow>}
  </Map>
}

export function EvidenceMap(props: EvidenceMapProps) {
  const { text: textUi } = useTextUi()

  const id = useId()
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY?.trim()
  const roles = props.demonstration ? ['CENTRE', 'BUSINESS', 'INSTITUTION', 'AMENITY'] as const : ['CENTRE', 'DIRECT_COMPETITOR', 'RELATED_BUSINESS'] as const
  return <section className="market-map-card" aria-labelledby={id}>
    <h2 id={id}><LocalizedText value={props.title} /></h2>
    <div className="map-legend" aria-label={textUi("Map legend")}>{roles.map(role => <span key={role}><i style={{ background: markerRoles[role].color }} aria-hidden="true" />{markerRoles[role].glyph} — <LocalizedText value={markerRoles[role].label} /></span>)}</div>
    <p className="map-provenance"><LocalizedText value={"Map visualization: Google Maps · Business evidence: "} />{props.demonstration ? textUi('Curated demonstration data') : props.evidenceProvider === 'GOOGLE_PLACES' ? 'Google Places' : <a href="https://www.openstreetmap.org/copyright"><LocalizedText value={"OpenStreetMap / Overpass"} /></a>}<LocalizedText value={" · Distance calculation: PostGIS"} /></p>
    <div className="market-map" role="region" aria-label={textUi(props.title)}>
      {!apiKey ? <MapMessage><LocalizedText value={"Google Maps is not configured for this environment."} /></MapMessage>
        : !validCoordinates(props.latitude, props.longitude) || !Number.isFinite(props.radiusMeters) || props.radiusMeters <= 0 ? <MapMessage><LocalizedText value={"Map location or radius is unavailable. Business evidence remains available below."} /></MapMessage>
        : <MapErrorBoundary><APIProvider apiKey={apiKey}><GoogleEvidenceMap {...props} /></APIProvider></MapErrorBoundary>}
    </div>
    <details className="map-alternative"><summary><LocalizedText value={props.textLabel} /></summary><p><LocalizedText value={"Analysis centre: "} />{props.centreName}<LocalizedText value={" · Selected radius: "} />{props.radiusMeters / 1000}<LocalizedText value={" km"} /></p>{!props.points.length && <p><LocalizedText value={"No mapped businesses found in this evidence."} /></p>}<ul>{props.points.map(point => <li key={point.id}><strong>{point.name}</strong> — <LocalizedText value={markerRoles[point.role].label} /> · <LocalizedText value={point.detail} /><LocalizedText value={" · Evidence source: "} /><LocalizedText value={point.source} /></li>)}</ul></details>
  </section>
}

export function MarketMap({ analysis }: { analysis: MarketAnalysis }) {
  const { text: textUi } = useTextUi()

  return <EvidenceMap latitude={analysis.selectedLocation.latitude} longitude={analysis.selectedLocation.longitude}
    centreName={analysis.selectedLocation.name} title={textUi("Demonstration market map")} radiusMeters={analysis.radiusKm * 1000} demonstration
    textLabel={textUi("View map evidence as text")} points={analysis.mapPoints.map((point, index) => ({ ...point, id: `${point.kind}-${index}`, role: point.kind, source: 'Curated demonstration data', detail: `${point.subtype.replaceAll('_', ' ')} · Distance: ${point.distanceKm} km` }))} />
}
