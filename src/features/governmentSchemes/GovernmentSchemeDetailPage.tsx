import { useCallback } from 'react'
import { isAxiosError } from 'axios'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import { useUi } from '../../i18n/uiContextValue'
import { governmentSchemeService } from '../../services/governmentSchemeService'
import { CatalogError, CatalogSkeleton, SchemeDetailContent } from './CatalogViews'
import { useCatalogRequest } from './useCatalogRequest'
export function GovernmentSchemeDetailPage() {
  const { slug = '' } = useParams()
  const [params] = useSearchParams()
  const { text } = useUi()
  const load = useCallback((signal: AbortSignal) => governmentSchemeService.detail(slug, signal), [slug])
  const detail = useCatalogRequest(slug, load)
  return <div className="gc-page gc-detail"><Link className="button button--outline" to={`/government-schemes${params.size ? `?${params}` : ''}`}>{text('Back to catalog')}</Link>
    {detail.loading ? <CatalogSkeleton label="Loading scheme details" /> : detail.error ? isAxiosError(detail.error) && detail.error.response?.status === 404 ? <h1>{text('Scheme not found.')}</h1> : <CatalogError label="Unable to load scheme details." retry={detail.retry} /> : detail.data && <SchemeDetailContent scheme={detail.data} />}
  </div>
}
