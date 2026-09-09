import type { NearbyMarketEvidence } from '../../types/nearbyMarket'

export interface NearbyState {
  query: string
  slug: string
  radius: number
  result: NearbyMarketEvidence | null
}
export const initialNearbyState: NearbyState = { query: '', slug: '', radius: 5, result: null }
export const normalizeBusinessQuery = (value: string) => value.trim().replace(/\s+/g, ' ')
export const validBusinessQuery = (value: string) => normalizeBusinessQuery(value).length >= 2 && normalizeBusinessQuery(value).length <= 200

type Action = { type: 'query'; value: string } | { type: 'business'; value: string } | { type: 'radius'; value: number } | { type: 'result'; value: NearbyMarketEvidence | null }

export function nearbyReducer(state: NearbyState, action: Action): NearbyState {
  if (action.type === 'query') return { ...state, query: action.value, slug: '' }
  if (action.type === 'business') return { ...state, slug: action.value, result: null }
  if (action.type === 'radius') return { ...state, radius: action.value }
  if (action.value && ((state.query ? action.value.business_query !== normalizeBusinessQuery(state.query) : action.value.business.slug !== state.slug) || action.value.radius.selected_km !== state.radius)) return state
  return { ...state, result: action.value }
}

export function proposedBusinessDefault(id: string | null | undefined, catalog: Array<{ id: string; slug: string }>) {
  const match = catalog.find(business => business.id === id)
  return { slug: match?.slug ?? '', unavailable: Boolean(id && !match) }
}

export function selectedCircleMeters(result: NearbyMarketEvidence): number[] {
  return [result.radius.selected_meters]
}
