import { apiClient } from './apiClient'

export interface AdminOverview {
  total_registered_users: number
  total_entrepreneurs: number
  profiles_pending: number
  new_enterprises: number
  existing_enterprises: number
  states_count: number
  districts_count: number
}
export async function getAdminOverview(signal?: AbortSignal): Promise<AdminOverview> {
  const response = await apiClient.get<AdminOverview>('/admin/overview', { signal })
  return response.data
}

export interface GeographicRow { entrepreneur_count: number; percentage: string; new_enterprises: number; existing_enterprises: number }
export interface StateRow extends GeographicRow { state: string; state_key: string; districts_count: number }
export interface StateAnalytics { total_entrepreneurs: number; located_entrepreneurs: number; missing_state_count: number; states_count: number; districts_count: number; states: StateRow[] }
export interface DistrictRow extends GeographicRow { district: string; district_key: string }
export interface DistrictAnalytics { state: string; state_key: string; total_entrepreneurs: number; districts_count: number; missing_district_count: number; new_enterprises: number; existing_enterprises: number; districts: DistrictRow[] }
export interface EntrepreneurItem { full_name: string; email: string; mobile_number: string; state: string | null; district: string | null; taluka: string | null; village: string | null; enterprise_status: 'new' | 'existing' | 'unspecified'; proposed_business: string | null; preferred_language: string; created_at: string; profile_status: 'complete' | 'created' | 'pending' }
export interface EntrepreneurPage { items: EntrepreneurItem[]; total: number; page: number; page_size: number; total_pages: number }
export async function getAdminData<T>(path: string, signal?: AbortSignal): Promise<T> {
  return (await apiClient.get<T>(`/admin/${path}`, { signal })).data
}
export function statePath(key: string) { return `/admin/analytics/geography/state/${encodeURIComponent(key)}` }
export function entrepreneursPath(state: string, district: string) { return `/admin/entrepreneurs?${new URLSearchParams({ state, district })}` }
