const filterKeys = ['search', 'state', 'district', 'enterprise_status', 'sort', 'page_size'] as const
export function entrepreneurQuery(params: URLSearchParams) {
  const clean = new URLSearchParams()
  for (const key of filterKeys) { const value = params.get(key); if (value) clean.set(key, value) }
  const page = Number(params.get('page') || 1)
  clean.set('page', String(Number.isSafeInteger(page) && page > 0 && page <= 1_000_000 ? page : 1))
  return clean
}
export function filtersQuery(data: FormData) {
  const params = new URLSearchParams()
  for (const key of filterKeys) { const value = String(data.get(key) ?? '').trim(); if (value) params.set(key, value) }
  params.set('page', '1')
  return params
}
export function pageQuery(params: URLSearchParams, page: number) { const next = entrepreneurQuery(params); next.set('page', String(page)); return next }

