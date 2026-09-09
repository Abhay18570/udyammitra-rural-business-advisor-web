import type { NearbyPOI } from '../../types/nearbyMarket'

export const markerRoles = {
  CENTRE: { label: 'Analysis centre', color: '#2563eb', glyph: 'C' },
  DIRECT_COMPETITOR: { label: 'Direct competitor', color: '#dc2626', glyph: 'D' },
  RELATED_BUSINESS: { label: 'Related business', color: '#b45309', glyph: 'R' },
  GENERIC_POI: { label: 'Uncertain relevance', color: '#64748b', glyph: '?' },
  BUSINESS: { label: 'Demo business', color: '#7c3aed', glyph: 'B' },
  INSTITUTION: { label: 'Demo institution', color: '#176b52', glyph: 'I' },
  AMENITY: { label: 'Demo amenity', color: '#475569', glyph: 'A' },
} as const
export interface EvidenceMapPoint {
  id: string; name: string; latitude: number; longitude: number
  role: Exclude<keyof typeof markerRoles, 'CENTRE'>; detail: string; source: string
}
export function nearbyMapPoints(points: NearbyPOI[]): EvidenceMapPoint[] {
  return points.map(p => ({ id: `${p.external_type}-${p.external_id}`, name: p.name,
    latitude: p.latitude, longitude: p.longitude, role: p.classification,
    detail: `Distance: ${p.distance_km} km`, source: p.provider === 'GOOGLE_PLACES' ? 'Google Places' : 'OpenStreetMap / Overpass' }))
}
export function validCoordinates(latitude: number, longitude: number) {
  return Number.isFinite(latitude) && Number.isFinite(longitude) && Math.abs(latitude) <= 90 && Math.abs(longitude) <= 180
}
