import { apiClient } from './apiClient'
import type { GovernmentSchemeDetail, GovernmentSchemeFilters, GovernmentSchemeListResponse, GovernmentSchemeQuery } from '../types/governmentScheme'
export const governmentSchemeService = {
  async list(params: GovernmentSchemeQuery, signal?: AbortSignal) {
    return (await apiClient.get<GovernmentSchemeListResponse>('/government-schemes', { params, signal })).data
  },
  async filters(signal?: AbortSignal) {
    return (await apiClient.get<GovernmentSchemeFilters>('/government-schemes/filters', { signal })).data
  },
  async detail(slug: string, signal?: AbortSignal) {
    return (await apiClient.get<GovernmentSchemeDetail>(`/government-schemes/${encodeURIComponent(slug)}`, { signal })).data
  },
}
