import type { SchemeAnalysis, SchemeGuidance } from '../types/scheme'
import { apiClient } from './apiClient'

// Keep explanation parameter keys stable for future translations/report consumers.
function fromWire(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(fromWire)
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [
      key.replace(/_([a-z0-9])/g, (_, character: string) => character.toUpperCase()),
      key === 'params' ? item : fromWire(item),
    ]))
  }
  return value
}

export const schemeService = {
  async guidance(signal?: AbortSignal): Promise<SchemeGuidance> {
    return fromWire((await apiClient.get('/schemes/guidance', { signal })).data) as SchemeGuidance
  },
  async analyze(financialAnalysisId: string, signal?: AbortSignal): Promise<SchemeAnalysis> {
    const response = await apiClient.post('/schemes/analyze', { financial_analysis_id: financialAnalysisId }, { signal })
    const result = fromWire(response.data) as SchemeAnalysis
    if (result.financialAnalysisId !== financialAnalysisId) throw new Error('Financial analysis response mismatch.')
    return result
  },
}
