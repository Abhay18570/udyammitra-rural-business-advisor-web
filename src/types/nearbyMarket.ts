export interface NearbyPOI {
  provider: string
  external_type: 'node' | 'way' | 'relation' | 'place'
  external_id: string
  name: string
  latitude: number
  longitude: number
  coordinate_kind: 'NODE' | 'REPRESENTATIVE_CENTER' | 'PLACE_LOCATION'
  classification: 'DIRECT_COMPETITOR' | 'RELATED_BUSINESS' | 'GENERIC_POI'
  matched_business_slug: string
  matching_rule: string
  matching_evidence: Array<{ key: string; value: string }>
  normalized_tags: Record<string, string>
  normalized_address: Record<string, string>
  fetched_at: string
  distance_meters: number
  distance_km: string
}

/** Provider evidence keys are preserved; unlike legacy demo data, tags are not camelized. */
export interface NearbyMarketEvidence {
  business_query?: string
  matched_catalog_business_slug?: string | null
  generic_pois?: NearbyPOI[]
  business: { id: string | null; slug: string | null; display_name: string }
  location: {
    latitude: number; longitude: number; display_name: string; query_used: string
    provider: string; precision: string; location_fingerprint: string
    fetched_at: string; expires_at: string; address: Record<string, string>
  }
  radius: { selected_km: number; selected_meters: number; distance_method: 'POSTGIS_GEOGRAPHY_SPHEROID' }
  summary: { direct_competitors: number; related_businesses: number; nearest_direct_competitor: NearbyPOI | null }
  competitors: NearbyPOI[]
  related_businesses: NearbyPOI[]
  source: { provider: string; mode: 'LIVE' | 'CACHE'; cache_status: 'FRESH_FETCH' | 'FRESH_CACHE' | 'STALE_CACHE'; fetched_at: string; expires_at: string; mapping_version: string }
  quality: { complete_query: boolean; rejected_record_count: number; warnings: Array<{ code: string; message: string }>; attribution: string }
}
