import { useUi as useTextUi } from '../../i18n/uiContextValue'
import { LocalizedText } from '../../i18n/LocalizedText'
import { Link } from 'react-router-dom'
import { useEffect, useRef, useState } from 'react'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Card } from '../../components/ui/Card'
import { Alert, LoadingState } from '../../components/ui/Feedback'
import { useUi } from '../../i18n/uiContextValue'
import { getApiErrorMessage } from '../../services/apiError'
import { schemeService } from '../../services/schemeService'
import type { SchemeAnalysis, SchemeExplanation } from '../../types/scheme'
import { formatINR } from '../../utils/inr'

function Explanations({ items }: { items: SchemeExplanation[] }) {
  return <ul>{items.map(item => <li key={item.code}><LocalizedText value={item.message} /></li>)}</ul>
}

/** Parent keys this panel by saved analysis and unmounts it whenever inputs change. */
export function SchemeEligibilityPanel({ financialAnalysisId }: { financialAnalysisId: string }) {
  const { text: textUi } = useTextUi()

  const { t } = useUi()
  const labels = t.schemeRouter
  const [result, setResult] = useState<SchemeAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const request = useRef<AbortController | null>(null)

  useEffect(() => () => { request.current?.abort() }, [financialAnalysisId])

  const analyze = async () => {
    request.current?.abort()
    const controller = new AbortController()
    request.current = controller
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const response = await schemeService.analyze(financialAnalysisId, controller.signal)
      if (!controller.signal.aborted && request.current === controller) setResult(response)
    } catch (reason) {
      if (!controller.signal.aborted && request.current === controller) setError(getApiErrorMessage(reason, labels.failure))
    } finally {
      if (!controller.signal.aborted && request.current === controller) setLoading(false)
    }
  }

  const current = result?.financialAnalysisId === financialAnalysisId ? result : null
  const money = (value: string) => formatINR(value, { fractionDigits: 2 })
  return (
    <Card className="scheme-panel" aria-busy={loading}>
      <h2><LocalizedText value={labels.title} /></h2>
      {!current && <Button type="button" onClick={() => void analyze()} disabled={loading}>{error ? labels.retry : labels.check}</Button>}
      {loading && <LoadingState label={textUi(labels.loading)} />}
      {error && <Alert tone="danger"><LocalizedText value={error} /></Alert>}
      {current && <div aria-live="polite">
        {current.scheme ? <header className="scheme-panel__heading">
          <h3>{current.scheme.displayName}</h3>
          <Badge tone={current.fullyCovered ? 'green' : 'orange'}>{current.fullyCovered ? labels.eligible : labels.gapStatus}</Badge>
        </header> : <Alert>{labels.unsupported}</Alert>}
        <dl className="scheme-panel__metrics">
          <div><dt>{labels.project}</dt><dd>{money(current.projectCost)}</dd></div>
          <div><dt>{labels.contribution}</dt><dd>{money(current.beneficiaryContribution)}</dd></div>
          <div><dt>{labels.requirement}</dt><dd>{money(current.financingRequirement)}</dd></div>
          {current.indicativeFinancedPrincipal !== null && <div><dt>{labels.principal}</dt><dd>{money(current.indicativeFinancedPrincipal)}</dd></div>}
          {current.scheme && <div><dt>{labels.cap}</dt><dd>{money(current.scheme.maximumLoanAmount)}</dd></div>}
        </dl>
        {current.schemeStatus === 'ELIGIBLE_WITH_GAP' && <section className="scheme-panel__gap" role="note">
          <h3>{labels.gap}: {money(current.schemeFinancingGap!)}</h3>
          <Explanations items={current.warnings} />
          <dl className="scheme-panel__metrics">
            <div><dt>{labels.additional}</dt><dd>{money(current.additionalContributionRequired!)}</dd></div>
            <div><dt>{labels.total}</dt><dd>{money(current.totalContributionRequired!)}</dd></div>
          </dl>
          <p>{labels.sameProject}</p>
        </section>}
        {current.scheme && <section>
          <h3>{labels.terms}</h3>
          <dl className="scheme-panel__metrics">
            <div><dt>{labels.interest}</dt><dd>{current.scheme.annualInterestRatePercent}%</dd></div>
            <div><dt>{labels.tenure}</dt><dd>{current.scheme.tenureMonths} {labels.months}</dd></div>
            <div><dt>{labels.moratorium}</dt><dd>{current.scheme.moratoriumMonths} {labels.months}</dd></div>
          </dl>
        </section>}
        <h3>{labels.why}</h3>
        <Explanations items={current.eligibilityReasons} />
        {current.schemeStatus !== 'ELIGIBLE_WITH_GAP' && <Explanations items={current.warnings} />}
        <Link className="button button--success" to={`/business-analysis?financial_analysis_id=${encodeURIComponent(financialAnalysisId)}`}><LocalizedText value={"Continue to Business Analysis"} /></Link>
        <h3>{labels.next}</h3>
        <Explanations items={current.nextSteps} />
        <p className="scheme-panel__notice"><LocalizedText value={current.disclaimer} /></p>
        {current.scheme && <footer>
          <Button type="button" disabled aria-describedby="repayment-coming">{labels.repayment}</Button>
          <p id="repayment-coming">{labels.coming}</p>
        </footer>}
      </div>}
    </Card>
  )
}
