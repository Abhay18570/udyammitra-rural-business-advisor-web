import { useUi } from '../../i18n/uiContextValue'
import type { AdminDataState } from './useAdminData'

export function AdminDataFeedback({ state, error, retry }: { state: AdminDataState<unknown>; error: string; retry: () => void }) {
  const { text } = useUi()
  if (state.status === 'ready') return null
  if (state.status === 'loading') return <div role="status" aria-busy="true" aria-label={text('Loading statistics')}><p>{text('Loading statistics')}</p><div className="officer-kpis" aria-hidden="true">{[1, 2, 3].map(key => <div key={key} className="officer-card officer-skeleton"><span /></div>)}</div><div className="officer-card officer-skeleton officer-chart-placeholder" aria-hidden="true" /><div className="officer-card officer-skeleton" aria-hidden="true"><span /><span /><span /></div></div>
  return <div role="alert" className="officer-notice"><p>{text(state.code === 403 ? 'You do not have permission to access the administration portal.' : state.code === 404 ? 'State not found.' : error)}</p>{state.code !== 403 && <button onClick={retry}>{text('Try again')}</button>}</div>
}
export function GeographicSummary({ cards }: { cards: Array<[string, number]> }) {
  const { text, language } = useUi()
  return <div className="officer-kpis">{cards.map(([label, count]) => <article className="officer-card" key={label}><h2>{text(label)}</h2><strong>{new Intl.NumberFormat(`${language}-IN`).format(count)}</strong></article>)}</div>
}
