import axios from 'axios'
import type { MarketAnalysis, MarketLocationsResponse } from '../types/market'
import { apiClient } from './apiClient'

const camelize = (key: string) => key.replace(/_([a-z0-9])/g, (_, character: string) => character.toUpperCase())
function fromWire<T>(value: unknown): T {
  if (Array.isArray(value)) return value.map(item => fromWire(item)) as T
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([key, item]) => [camelize(key), fromWire(item)])) as T
  return value as T
}

export const marketService = {
  async locations(): Promise<MarketLocationsResponse> { return fromWire((await apiClient.get('/market/locations')).data) },
  async run(radiusKm: 5 | 10, demoLocationSlug?: string): Promise<MarketAnalysis> { return fromWire((await apiClient.post('/market/analysis', { radius_km: radiusKm, demo_location_slug: demoLocationSlug || undefined })).data) },
  async latest(): Promise<MarketAnalysis | null> { try { return fromWire((await apiClient.get('/market/analyses/latest')).data) } catch (error) { if (axios.isAxiosError(error) && error.response?.status === 404) return null; throw error } },
  async get(id: string): Promise<MarketAnalysis> { return fromWire((await apiClient.get(`/market/analyses/${encodeURIComponent(id)}`)).data) },
}
