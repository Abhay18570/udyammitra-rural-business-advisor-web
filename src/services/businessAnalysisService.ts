import { apiClient } from './apiClient'
import type { BusinessAnalysis } from '../types/businessAnalysis'
export const businessAnalysisService = {
  async analyze(financialId: string, radius: number, signal?: AbortSignal): Promise<BusinessAnalysis> {
    return (await apiClient.post<BusinessAnalysis>('/business-analysis', { financial_analysis_id: financialId, radius_km: radius }, { signal, timeout: 60000 })).data
  },
  async get(id: string, signal?: AbortSignal): Promise<BusinessAnalysis> {
    return (await apiClient.get<BusinessAnalysis>(`/business-analysis/${encodeURIComponent(id)}`, { signal })).data
  },
}
