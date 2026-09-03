import axios from 'axios'
import type { FinancialAnalysis } from '../types/financial'
import { apiClient } from './apiClient'

const camelize = (key: string) => key.replace(/_([a-z0-9])/g, (_, character: string) => character.toUpperCase())
function fromWire<T>(value: unknown): T { if (Array.isArray(value)) return value.map(fromWire) as T; if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([key, item]) => [camelize(key), fromWire(item)])) as T; return value as T }
export const financialService = {
  async analyze(businessSlug: string, availableMarginCapital: string, feasibilityAnalysisId?: string): Promise<FinancialAnalysis> { return fromWire((await apiClient.post('/financial/analyze', { business_slug: businessSlug, available_margin_capital: availableMarginCapital, feasibility_analysis_id: feasibilityAnalysisId })).data) },
  async latest(businessSlug?: string): Promise<FinancialAnalysis | null> { try { return fromWire((await apiClient.get('/financial/latest', { params: { business_slug: businessSlug } })).data) } catch (error) { if (axios.isAxiosError(error) && error.response?.status === 404) return null; throw error } },
  async get(id: string): Promise<FinancialAnalysis> { return fromWire((await apiClient.get(`/financial/${encodeURIComponent(id)}`)).data) },
}
