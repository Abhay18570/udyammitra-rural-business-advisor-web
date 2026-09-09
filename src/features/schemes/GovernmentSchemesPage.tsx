import { useEffect, useState, useRef } from 'react'
import { Link } from 'react-router-dom'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Alert, LoadingState } from '../../components/ui/Feedback'
import { useUi } from '../../i18n/uiContextValue'
import { schemeService } from '../../services/schemeService'
import type { SchemeGuidance, SchemeMetadata } from '../../types/scheme'
import { formatINR } from '../../utils/inr'

export function GovernmentSchemesPage() {
  const { text, t } = useUi()
  const [data, setData] = useState<SchemeGuidance | null>(null)
  const [loading, setLoading] = useState(true)
  const [failed, setFailed] = useState(false)
  const [attempt, setAttempt] = useState(0)
  const controllerRef = useRef<AbortController | null>(null)

  useEffect(() => {
    const controller = new AbortController()
    controllerRef.current = controller

    schemeService.guidance(controller.signal)
      .then(result => {
        if (!controller.signal.aborted) {
          setData(result)
          setFailed(false)
          setLoading(false)
        }
      })
      .catch(() => {
        if (!controller.signal.aborted) {
          setFailed(true)
          setLoading(false)
        }
      })

    return () => {
      controller.abort()
    }
  }, [attempt])

  const handleRetry = () => {
    setLoading(true)
    setFailed(false)
    setAttempt(prev => prev + 1)
  }

  return (
    <section className="business-analysis-page analysis-sections">
      {/* SECTION 1: Government Schemes Header */}
      <header className="financial-heading">
        <span className="eyebrow">{text('Smart Scheme Guidance')}</span>
        <h1>{text('Government Schemes')}</h1>
        <p>{text('Understand applicable financing pathways based on project requirements and current scheme rules. Guidance does not guarantee eligibility or sanction.')}</p>
      </header>

      {loading ? (
        <LoadingState label={text(t.schemeRouter.loading)} />
      ) : failed ? (
        <Card>
          <Alert tone="danger">{text('Unable to load scheme guidance. Please retry or review your Financial Plan.')}</Alert>
          <div style={{ marginTop: '16px', display: 'flex', gap: '12px', alignItems: 'center' }}>
            <Button onClick={handleRetry}>{t.schemeRouter.retry}</Button>
            <Link className="button button--outline" to="/financial-plan">{text('Review Financial Plan')}</Link>
          </div>
        </Card>
      ) : data ? (
        <SchemeGuidanceView data={data} />
      ) : null}
    </section>
  )
}

export function SchemeGuidanceView({ data }: { data: SchemeGuidance }) {
  const { text, t, date } = useUi()
  const labels = t.schemeRouter
  const result = data.result
  const isIllustration = data.source === 'PROFILE_ILLUSTRATION'
  const [expandedSchemes, setExpandedSchemes] = useState<Record<string, boolean>>({})

  const toggleDetail = (type: string) => {
    setExpandedSchemes(prev => ({ ...prev, [type]: !prev[type] }))
  }

  const money = (value: string | null | undefined) =>
    value === null || value === undefined ? '—' : formatINR(value, { fractionDigits: 2, fallback: text('Not available') })

  const metric = (label: string, value: string | number | React.ReactNode, key?: string) => (
    <div key={key || label}>
      <dt>{text(label)}</dt>
      <dd>{value}</dd>
    </div>
  )

  const name = (rule: SchemeMetadata) => text(rule.displayName)

  const range = (rule: SchemeMetadata) =>
    `${rule.projectCostMinInclusive ? '≥' : '>'} ${money(rule.projectCostMin)} · ${rule.projectCostMaxInclusive ? '≤' : '<'} ${money(rule.projectCostMax)}`

  const terms = (rule: SchemeMetadata) => (
    <dl className="scheme-panel__metrics">
      {metric('Applicable Project Cost', range(rule))}
      {metric('Maximum Scheme Loan', money(rule.maximumLoanAmount))}
      {metric('Interest Rate', `${rule.annualInterestRatePercent}%`)}
      {metric('Tenure', `${rule.tenureMonths} ${labels.months}`)}
      {metric('Moratorium', `${rule.moratoriumMonths} ${labels.months}`)}
    </dl>
  )

  const microRule = data.rules.find(r => r.type === 'MICRO_FINANCE') ?? data.rules[0]
  const termRule = data.rules.find(r => r.type === 'TERM_LOAN') ?? data.rules[1]

  const isMicroRecommended = result?.scheme?.type === 'MICRO_FINANCE'
  const isTermRecommended = result?.scheme?.type === 'TERM_LOAN'

  const getSchemeReason = (rule: SchemeMetadata) => {
    if (!result || !result.scheme) {
      return text('Your project cost exceeds the supported project-cost range.')
    }
    if (rule.type === result.scheme.type) {
      return text(`Your project cost falls within the ${rule.displayName} range.`)
    }
    if (rule.type === 'MICRO_FINANCE') {
      return text('Your project cost exceeds the ₹1.40 lakh Micro Finance limit.')
    }
    return text('Your project cost falls within the Micro Finance range.')
  }

  const getSchemeSuitability = (rule: SchemeMetadata) => {
    if (rule.type === 'MICRO_FINANCE') {
      return text('Micro-enterprises and village units with total project cost up to ₹1.40 lakh seeking concessional working or asset finance.')
    }
    return text('Rural businesses and small manufacturing or service enterprises requiring medium-to-large project investment between ₹1.40 lakh and ₹50 lakh.')
  }

  return (
    <>
      {isIllustration && (
        <Alert tone="info">
          {text('Illustrative estimate only. Complete your Financial Plan for exact scheme eligibility and funding-gap calculation.')}
        </Alert>
      )}

      {/* SECTION 2: Your Financing Position */}
      <Card className="scheme-panel">
        <h2>{text('Your Financing Position')}</h2>
        {!result ? (
          <div>
            <p>{text('Your financial information is incomplete.')}</p>
            {data.notice === 'CONTRIBUTION_UNUSABLE' && (
              <p>{text('Your Profile contribution is missing or invalid. Review Profile or complete a Financial Plan.')}</p>
            )}
            <p>{text('Complete your Financial Plan to receive personalized scheme guidance.')}</p>
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginTop: '16px' }}>
              <Link className="button button--primary" to="/financial-plan">
                {text('Complete Financial Plan')}
              </Link>
              <Link className="button button--outline" to="/profile">
                {text('Review Profile')}
              </Link>
            </div>
          </div>
        ) : (
          <>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginBottom: '16px' }}>
              <p style={{ margin: 0 }}>
                {text('Calculation Source')}: <strong>{text(isIllustration ? 'Profile-based estimate' : 'Saved Financial Plan')}</strong>
              </p>
              {result.business && (
                <p style={{ margin: 0 }}>
                  {text('Proposed Business')}: <strong>{result.business.name}</strong>
                </p>
              )}
              {data.sourceObservedAt && (
                <p style={{ margin: 0, color: 'var(--muted)', fontSize: '13px' }}>
                  {text('Source updated')}: {date(data.sourceObservedAt)}
                </p>
              )}
            </div>

            <dl className="scheme-panel__metrics">
              {isIllustration ? (
                <>
                  {metric('Available Contribution', money(result.beneficiaryContribution))}
                  {metric('Illustrative Project Capacity', money(result.projectCost))}
                  {metric('Indicative Funding', money(result.financingRequirement))}
                </>
              ) : (
                <>
                  {metric('Your Project Cost', money(result.projectCost))}
                  {metric('Your Contribution', money(result.beneficiaryContribution))}
                  {metric('Loan Requirement', money(result.financingRequirement))}
                  {data.setupFundingGap !== null && Number(data.setupFundingGap) > 0 && (
                    metric('Business Setup Shortfall', money(data.setupFundingGap))
                  )}
                </>
              )}
            </dl>

            {isIllustration && (
              <p style={{ marginTop: '12px', fontSize: '14px', color: 'var(--muted)' }}>
                {text('Complete your Financial Plan for exact scheme guidance.')}
              </p>
            )}
          </>
        )}
      </Card>

      {/* SECTION 3: Recommended Scheme */}
      {result && (
        <Card className="scheme-panel scheme-panel--recommended">
          {result.scheme ? (
            <>
              <h2>{text(isIllustration ? 'Indicative Scheme Tier' : 'Recommended Scheme')}</h2>
              <header className="scheme-panel__heading">
                <h3 style={{ fontSize: '22px', margin: 0 }}>{name(result.scheme)}</h3>
                {isIllustration ? (
                  <Badge tone="navy">{text('Illustrative Estimate')}</Badge>
                ) : result.schemeStatus === 'ELIGIBLE' ? (
                  <Badge tone="green">{text('Eligible')}</Badge>
                ) : result.schemeStatus === 'ELIGIBLE_WITH_GAP' ? (
                  <Badge tone="orange">{text('Eligible with additional contribution')}</Badge>
                ) : (
                  <Badge tone="orange">{text('Additional own contribution required')}</Badge>
                )}
              </header>

              <section style={{ marginTop: '18px' }}>
                <h4 style={{ fontSize: '14px', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  {labels.terms}
                </h4>
                {terms(result.scheme)}
              </section>

              <section style={{ marginTop: '18px' }}>
                <h4 style={{ fontSize: '14px', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  {text('Your Financing Breakdown')}
                </h4>
                <dl className="scheme-panel__metrics">
                  {metric('Your Project Cost', money(result.projectCost))}
                  {metric('Loan Requirement', money(result.financingRequirement))}
                  {metric('Indicative Scheme Loan', money(result.indicativeFinancedPrincipal))}
                  {metric('Funding Gap', money(result.schemeFinancingGap))}
                  {result.additionalContributionRequired && Number(result.additionalContributionRequired) > 0 && (
                    <>
                      {metric('Additional Contribution', money(result.additionalContributionRequired))}
                      {metric('Total Contribution for the Same Project', money(result.totalContributionRequired))}
                    </>
                  )}
                </dl>
                {result.schemeStatus === 'ELIGIBLE_WITH_GAP' && (
                  <p style={{ fontSize: '13px', color: 'var(--muted)' }}>{text(labels.sameProject)}</p>
                )}
              </section>

              <section style={{ marginTop: '14px' }}>
                <p><strong>{text('Why this scheme?')}</strong></p>
                <ul>
                  {result.eligibilityReasons.map(item => (
                    <li key={item.code}>{text(item.message)}</li>
                  ))}
                </ul>
              </section>
            </>
          ) : (
            <Alert tone="info">
              <h3>{text('Outside supported scheme range')}</h3>
              <p>{text('Your project cost exceeds the supported limit for the schemes currently covered by UdyamMitra.')}</p>
              <dl className="scheme-panel__metrics" style={{ marginTop: '14px' }}>
                {metric('Your Project Cost', money(result.projectCost))}
                {metric('Supported maximum', money(data.rules[data.rules.length - 1]?.projectCostMax ?? '5000000.00'))}
              </dl>
              <div style={{ marginTop: '14px' }}>
                <Link className="button button--primary" to="/financial-plan">
                  {text('Review Financial Plan')}
                </Link>
              </div>
            </Alert>
          )}
        </Card>
      )}

      {/* SECTION 4: All Available Schemes */}
      <Card className="scheme-panel">
        <h2>{text('All Available Schemes')}</h2>
        <p style={{ color: 'var(--muted)', margin: '0 0 16px' }}>
          {text('Inspect both supported schemes below to understand terms, eligibility criteria, and applicability for your project.')}
        </p>

        <div className="scheme-grid">
          {data.rules.map(rule => {
            const isRec = result?.scheme?.type === rule.type
            const isExpanded = !!expandedSchemes[rule.type]
            const reasonText = getSchemeReason(rule)
            const suitabilityText = getSchemeSuitability(rule)

            return (
              <article
                key={rule.type}
                className={`scheme-card ${isRec ? 'scheme-card--recommended' : 'scheme-card--other'}`}
              >
                <header className="scheme-card__header">
                  <div>
                    <h3>{name(rule)}</h3>
                    <p className="scheme-card__sub">
                      {rule.type === 'MICRO_FINANCE'
                        ? text('Up to ₹1.40 lakh')
                        : text('Above ₹1.40 lakh up to ₹50 lakh')}
                    </p>
                  </div>
                  {isRec ? (
                    isIllustration ? (
                      <Badge tone="navy">{text('Illustrative Estimate')}</Badge>
                    ) : result?.schemeStatus === 'ELIGIBLE' ? (
                      <Badge tone="green">{text('Eligible')}</Badge>
                    ) : (
                      <Badge tone="orange">{text('Eligible with additional contribution')}</Badge>
                    )
                  ) : (
                    <Badge tone="navy">{text('Not Applicable')}</Badge>
                  )}
                </header>

                <dl className="scheme-card__metrics">
                  <div>
                    <dt>{text('Applicable Project Cost')}</dt>
                    <dd>{range(rule)}</dd>
                  </div>
                  <div>
                    <dt>{text('Maximum Scheme Loan')}</dt>
                    <dd>{money(rule.maximumLoanAmount)}</dd>
                  </div>
                  <div>
                    <dt>{text('Interest Rate')}</dt>
                    <dd>{rule.annualInterestRatePercent}%</dd>
                  </div>
                  <div>
                    <dt>{text('Tenure')}</dt>
                    <dd>{rule.tenureMonths} {labels.months}</dd>
                  </div>
                  <div>
                    <dt>{text('Moratorium')}</dt>
                    <dd>{rule.moratoriumMonths} {labels.months}</dd>
                  </div>
                  <div>
                    <dt>{text('Status')}</dt>
                    <dd>{isRec ? text('Recommended') : text('Not Applicable')}</dd>
                  </div>
                </dl>

                <div className="scheme-card__status">
                  <strong>{text('Status')}: </strong>
                  <span>{reasonText}</span>
                </div>

                {isRec && result && (
                  <div style={{ background: '#f0f7f4', padding: '10px 12px', borderRadius: '6px', margin: '8px 0 14px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '4px' }}>
                      <span style={{ color: '#31654e', fontWeight: 600 }}>{text('Indicative Scheme Loan')}:</span>
                      <strong style={{ color: '#17402f' }}>{money(result.indicativeFinancedPrincipal)}</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                      <span style={{ color: '#31654e', fontWeight: 600 }}>{text('Funding Gap')}:</span>
                      <strong style={{ color: '#17402f' }}>{money(result.schemeFinancingGap)}</strong>
                    </div>
                  </div>
                )}

                <div style={{ marginTop: 'auto', paddingTop: '10px' }}>
                  <Button
                    variant="outline"
                    onClick={() => toggleDetail(rule.type)}
                    aria-expanded={isExpanded}
                    aria-controls={`scheme-detail-${rule.type}`}
                  >
                    {isExpanded ? text('Hide Details') : text('View Details')}
                  </Button>
                </div>

                {isExpanded && (
                  <section id={`scheme-detail-${rule.type}`} className="scheme-card__drawer">
                    <div className="scheme-card__section">
                      <h4>{text('Scheme Overview')}</h4>
                      <p>{suitabilityText}</p>
                    </div>

                    <div className="scheme-card__section">
                      <h4>{text('Scheme Rule')}</h4>
                      <dl className="scheme-panel__metrics" style={{ margin: '8px 0' }}>
                        {metric('Applicable Project Cost', range(rule))}
                        {metric('Funding Support', text('Up to 90%'))}
                        {metric('Maximum Scheme Loan', money(rule.maximumLoanAmount))}
                        {metric('Beneficiary Contribution', text('Minimum 10%'))}
                        {metric('Interest Rate', `${rule.annualInterestRatePercent}%`)}
                        {metric('Repayment Tenure', `${rule.tenureMonths} ${labels.months}`)}
                        {metric('Moratorium', `${rule.moratoriumMonths} ${labels.months}`)}
                      </dl>
                    </div>

                    <div className="scheme-card__section">
                      <h4>{text('Your Case')}</h4>
                      <dl className="scheme-card__case-grid">
                        {metric('Current User Project Cost', money(result?.projectCost))}
                        {metric('Loan Requirement', money(result?.financingRequirement))}
                        {metric('Indicative Loan for User', isRec ? money(result?.indicativeFinancedPrincipal) : '—')}
                        {metric('Funding Gap if any', isRec ? money(result?.schemeFinancingGap) : '—')}
                        {metric('Current Project Applicability', isRec ? text('Eligible') : text('Not Applicable'))}
                      </dl>
                      <p style={{ marginTop: '8px', fontSize: '12px', color: 'var(--muted)' }}>
                        <strong>{text('Reason')}: </strong>{reasonText}
                      </p>
                    </div>

                    <div className="scheme-card__section">
                      <h4>{text('Important Notes')}</h4>
                      <p style={{ fontSize: '12px', color: 'var(--muted)' }}>
                        {text('Subject to lender appraisal, credit history, and operational guidelines. Sanction is at the sole discretion of the lending institution.')}
                      </p>
                    </div>
                  </section>
                )}
              </article>
            )
          })}
        </div>
      </Card>

      {/* SECTION 5: Compare Schemes */}
      <Card className="scheme-panel">
        <h2>{text('Compare Schemes')}</h2>
        <div className="scheme-comparison-wrap">
          <table className="scheme-comparison-table">
            <thead>
              <tr>
                <th>{text('Feature')}</th>
                <th className={isMicroRecommended ? 'highlight-col' : ''}>{name(microRule)}</th>
                <th className={isTermRecommended ? 'highlight-col' : ''}>{name(termRule)}</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>{text('Applicable Project Cost')}</strong></td>
                <td className={isMicroRecommended ? 'highlight-col' : ''}>{text('Up to ₹1.40 lakh')}</td>
                <td className={isTermRecommended ? 'highlight-col' : ''}>{text('Above ₹1.40 lakh up to ₹50 lakh')}</td>
              </tr>
              <tr>
                <td><strong>{text('Funding Support')}</strong></td>
                <td className={isMicroRecommended ? 'highlight-col' : ''}>{text('Up to 90%')}</td>
                <td className={isTermRecommended ? 'highlight-col' : ''}>{text('Up to 90%')}</td>
              </tr>
              <tr>
                <td><strong>{text('Maximum Scheme Loan')}</strong></td>
                <td className={isMicroRecommended ? 'highlight-col' : ''}>{money(microRule.maximumLoanAmount)}</td>
                <td className={isTermRecommended ? 'highlight-col' : ''}>{money(termRule.maximumLoanAmount)}</td>
              </tr>
              <tr>
                <td><strong>{text('Interest Rate')}</strong></td>
                <td className={isMicroRecommended ? 'highlight-col' : ''}>{microRule.annualInterestRatePercent}%</td>
                <td className={isTermRecommended ? 'highlight-col' : ''}>{termRule.annualInterestRatePercent}%</td>
              </tr>
              <tr>
                <td><strong>{text('Tenure')}</strong></td>
                <td className={isMicroRecommended ? 'highlight-col' : ''}>{microRule.tenureMonths} {labels.months}</td>
                <td className={isTermRecommended ? 'highlight-col' : ''}>{termRule.tenureMonths} {labels.months}</td>
              </tr>
              <tr>
                <td><strong>{text('Moratorium')}</strong></td>
                <td className={isMicroRecommended ? 'highlight-col' : ''}>{microRule.moratoriumMonths} {labels.months}</td>
                <td className={isTermRecommended ? 'highlight-col' : ''}>{termRule.moratoriumMonths} {labels.months}</td>
              </tr>
              <tr>
                <td><strong>{text('Current Status')}</strong></td>
                <td className={isMicroRecommended ? 'highlight-col' : ''}>
                  {isMicroRecommended ? text('Eligible') : text('Not Applicable')}
                </td>
                <td className={isTermRecommended ? 'highlight-col' : ''}>
                  {isTermRecommended ? text('Eligible') : text('Not Applicable')}
                </td>
              </tr>
              <tr>
                <td><strong>{text('Recommended')}</strong></td>
                <td className={isMicroRecommended ? 'highlight-col' : ''}>
                  {isMicroRecommended ? text('Yes') : text('No')}
                </td>
                <td className={isTermRecommended ? 'highlight-col' : ''}>
                  {isTermRecommended ? text('Yes') : text('No')}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      {/* SECTION 6: How Recommendation Was Calculated */}
      {result && (
        <Card className="scheme-panel">
          <h2>{text('How This Was Calculated')}</h2>

          <p><strong>{text('Why this scheme?')}</strong></p>
          <ul>
            {result.eligibilityReasons.map(item => (
              <li key={item.code}>{text(item.message)}</li>
            ))}
          </ul>

          <div style={{ background: 'var(--surface)', padding: '16px', borderRadius: '8px', margin: '16px 0' }}>
            <dl className="scheme-panel__metrics" style={{ margin: 0 }}>
              {metric('Your Project Cost', money(result.projectCost))}
              {metric('Your Contribution', money(result.beneficiaryContribution))}
              {metric('Loan Requirement', money(result.financingRequirement))}
              {result.scheme && metric('Scheme Maximum', money(result.scheme.maximumLoanAmount))}
              {result.scheme && metric('Indicative Scheme Loan', money(result.indicativeFinancedPrincipal))}
              {result.scheme && metric('Funding Gap', money(result.schemeFinancingGap))}
            </dl>
          </div>

          <p>{text('The scheme can support up to 90% of the project cost, subject to the scheme loan limit.')}</p>
          <p>{text('Funding share, subject to the scheme loan cap')}: {data.fundingSharePercent}%</p>
          <p>{text('Original contribution share')}: {data.contributionSharePercent}%</p>

          {result.warnings.length > 0 && (
            <div style={{ marginTop: '12px' }}>
              <ul>
                {result.warnings.map(item => (
                  <li key={item.code} style={{ color: '#a94d0d' }}>
                    <strong>{text(item.message)}</strong>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.nextSteps.filter(item => item.code !== 'VERIFY_LENDER_TERMS').length > 0 && (
            <ul style={{ marginTop: '12px' }}>
              {result.nextSteps.filter(item => item.code !== 'VERIFY_LENDER_TERMS').map(item => (
                <li key={item.code}>{text(item.message)}</li>
              ))}
            </ul>
          )}
        </Card>
      )}

      {/* SECTION 7: Guidance / Next Step */}
      <Card className="scheme-panel">
        <h2>{text('Guidance / Next Step')}</h2>
        <p>
          {text(
            isIllustration
              ? 'Complete your Financial Plan for exact scheme guidance.'
              : 'Verify eligibility and terms with the lender before applying.'
          )}
        </p>
        <div style={{ marginTop: '16px' }}>
          <Link className="button button--primary" to="/financial-plan">
            {text(isIllustration ? 'Complete Financial Plan' : 'Review Financial Plan')}
          </Link>
        </div>
      </Card>

      {/* SECTION 8: Scheme Rules Used by UdyamMitra & Important Disclaimer */}
      <Card className="scheme-panel">
        <h2>{text('Scheme rules used by UdyamMitra')}</h2>
        <p style={{ color: 'var(--muted)', fontSize: '13px' }}>{data.schemeRulesVersion}</p>
        {data.rules.map(rule => (
          <section key={rule.type} style={{ marginTop: '16px', borderTop: '1px solid var(--line)', paddingTop: '16px' }}>
            <h3 style={{ margin: '0 0 8px' }}>{name(rule)}</h3>
            {terms(rule)}
          </section>
        ))}
        <div className="scheme-disclaimer" style={{ marginTop: '24px' }}>
          <div style={{ width: '100%' }}>
            <h3 style={{ fontSize: '14px', margin: '0 0 6px', color: 'var(--ink)' }}>{text('Important Disclaimer')}</h3>
            <p style={{ margin: 0 }}>{text(data.disclaimer)}</p>
          </div>
        </div>
      </Card>
    </>
  )
}
