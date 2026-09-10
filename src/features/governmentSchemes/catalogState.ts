import type { CatalogSort, GovernmentSchemeQuery, VerificationStatus } from '../../types/governmentScheme'
export const sorts: CatalogSort[] = ['name_asc', 'name_desc', 'newest', 'oldest']
const statuses: VerificationStatus[] = ['DATASET_ONLY', 'OFFICIAL_SOURCE_LINKED', 'VERIFIED', 'STALE']
export function readCatalogQuery(params: URLSearchParams): GovernmentSchemeQuery {
  const page = Number(params.get('page') || 1)
  const level = params.get('level')
  const status = params.get('verification_status') as VerificationStatus
  const sort = params.get('sort') as CatalogSort
  return {
    page: Number.isInteger(page) && page > 0 && page <= 2147483647 ? page : 1, page_size: 20,
    sort: sorts.includes(sort) ? sort : 'name_asc',
    search: params.get('search')?.trim().slice(0, 200) || undefined,
    level: level === 'CENTRAL' || level === 'STATE' ? level : undefined,
    state: level === 'CENTRAL' ? undefined : params.get('state')?.trim().slice(0, 100) || undefined,
    category: params.get('category')?.trim().slice(0, 200) || undefined,
    verification_status: statuses.includes(status) ? status : undefined,
  }
}
export function updateCatalogQuery(current: URLSearchParams, key: string, value: string): URLSearchParams {
  const next = new URLSearchParams(current)
  if (value) next.set(key, value); else next.delete(key)
  if (key !== 'page') next.set('page', '1')
  if (key === 'level' && value === 'CENTRAL') next.delete('state')
  return next
}
export function debounceCatalogSearch(callback: () => void): () => void {
  const timer = setTimeout(callback, 400)
  return () => clearTimeout(timer)
}
