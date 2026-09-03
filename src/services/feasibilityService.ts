import axios from 'axios'
import type { FeasibilityAnalysis } from '../types/feasibility'
import { apiClient } from './apiClient'

const camelize = (key: string) => key.replace(/_([a-z0-9])/g, (_, character: string) => character.toUpperCase())
function fromWire<T>(value: unknown): T {
  if (Array.isArray(value)) return value.map(item => fromWire(item)) as T
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([key, item]) => [camelize(key), fromWire(item)])) as T
  return value as T
}
export const feasibilityService = {
  async analyze(marketAnalysisId?: string): Promise<FeasibilityAnalysis> { return fromWire((await apiClient.post('/feasibility/analyze', { market_analysis_id: marketAnalysisId })).data) },
  async latest(): Promise<FeasibilityAnalysis | null> { try { return fromWire((await apiClient.get('/feasibility/latest')).data) } catch (error) { if (axios.isAxiosError(error) && error.response?.status === 404) return null; throw error } },
  async get(id: string): Promise<FeasibilityAnalysis> { return fromWire((await apiClient.get(`/feasibility/${encodeURIComponent(id)}`)).data) },
}
