import { useUi } from '../../i18n/uiContextValue'
import { Button } from '../../components/ui/Button'
import { formatINR } from '../../utils/inr'
import type { FinancialAnalysis } from '../../types/financial'

export function BusinessOverview({ financial, radius, running, hasAnalysis, onRadius, onGenerate }: { financial: FinancialAnalysis | null; radius: number; running: boolean; hasAnalysis: boolean; onRadius: (value: number) => void; onGenerate: () => void }) {
  const { text } = useUi()
  return <section className="profile-card business-overview"><h2>{text('Business Overview')}</h2>
    {financial ? <><span className="business-overview-label">{text('Business')}</span><h3>{financial.business.name}</h3>
      <dl className="business-overview-metrics"><div><dt>{text('Your Contribution')}</dt><dd>{formatINR(financial.availableMarginCapital, { fractionDigits: 2 })}</dd><small>{text('Saved financial margin')}</small></div><div><dt>{text('Estimated Project Capacity')}</dt><dd>{formatINR(financial.feasibleProjectCost, { fractionDigits: 2 })}</dd><small>{text('Planning value, not sanctioned finance')}</small></div></dl>
      <div className="business-overview-actions"><label>{text('Market Radius')}<select value={radius} disabled={running} onChange={event => onRadius(Number(event.target.value))}>{Array.from({ length: 10 }, (_, index) => index + 1).map(value => <option key={value} value={value}>{value} {text('km')}</option>)}</select></label>
      <Button disabled={running} onClick={onGenerate}>{text(running ? 'Analysing evidence…' : hasAnalysis ? 'Refresh Business Analysis' : 'Generate Business Analysis')}</Button></div>
    </> : <p>{text('Save a financial plan for your proposed business first.')}</p>}
  </section>
}
