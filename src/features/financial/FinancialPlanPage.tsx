import { useUi as useTextUi } from '../../i18n/uiContextValue'
import { LocalizedText, LocalizedDate } from '../../i18n/LocalizedText'
import {
  AlertCircle,
  ArrowLeft,
  ArrowRight,
  Calculator,
  CheckCircle2,
  Info,
  LoaderCircle,
  RotateCcw,
  Scale,
  ShieldAlert,
  ShieldCheck,
  TrendingUp,
} from 'lucide-react'
import { type FormEvent, useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { SchemeEligibilityPanel } from './SchemeEligibilityPanel'
import { useUi } from '../../i18n/uiContextValue'
import { Button } from '../../components/ui/Button'
import { getApiErrorMessage } from '../../services/apiError'
import { businessService } from '../../services/businessService'
import { feasibilityService } from '../../services/feasibilityService'
import { financialService } from '../../services/financialService'
import { profileService } from '../../services/profileService'
import type { BusinessDetail, BusinessListItem } from '../../types/business'
import type { FeasibilityAnalysis } from '../../types/feasibility'
import type { FinancialAnalysis } from '../../types/financial'
import type { EntrepreneurProfile } from '../../types/profile'
import { formatINR, parseINRToPaise } from '../../utils/inr'
import { categoryLabels, moneyRange } from '../businessCatalog/businessFormatters'

export function FinancialPlanPage() {
  const { businessId } = useParams()
  if (!businessId) return <BusinessSelection />
  return <FinancialCalculator key={businessId} businessId={businessId} />
}

function BusinessSelection() {
  const [businesses, setBusinesses] = useState<BusinessListItem[]>([])
  const [feasibility, setFeasibility] = useState<FeasibilityAnalysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    void Promise.all([businessService.list(), feasibilityService.latest()])
      .then(([items, analysis]) => {
        setBusinesses(items)
        setFeasibility(analysis)
      })
      .catch(reason => setError(getApiErrorMessage(reason, 'Unable to load businesses for financial planning.')))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="financial-page">
        <div className="financial-loading">
          <LoaderCircle className="spin" /><LocalizedText value={" Loading businesses… "} /></div>
      </div>
    )
  }

  return (
    <div className="financial-page">
      <header className="financial-heading">
        <span className="eyebrow"><LocalizedText value={"Financial structuring foundation"} /></span>
        <h1><LocalizedText value={"Choose a Business to Plan"} /></h1>
        <p><LocalizedText value={"Select a supported business before entering your available margin capital."} /></p>
      </header>

      {error && (
        <div className="financial-error" role="alert">
          <AlertCircle aria-hidden="true" />
          <span><LocalizedText value={error} /></span>
        </div>
      )}

      {feasibility?.topMatches.length ? (
        <section className="financial-selection">
          <div className="section-title-wrap">
            <h2><LocalizedText value={"Top Feasibility Matches"} /></h2>
            <span className="badge badge--success"><LocalizedText value={"From your saved feasibility analysis"} /></span>
          </div>
          <div className="financial-business-grid">
            {feasibility.topMatches.map(item => (
              <article key={item.businessId} className="financial-business-card">
                <div className="card-top">
                  <span className="badge badge--primary"><LocalizedText value={"Rank "} />{item.rank}</span>
                  <small className="feasibility-tag"><LocalizedText value={item.feasibilityLabel.replaceAll('_', ' ')} /></small>
                </div>
                <h3>{item.businessName}</h3>
                <p><LocalizedText value={item.shortDescription} /></p>
                <div className="card-footer">
                  <Link className="button button--primary button--sm" to={`/financial-plan/${item.businessSlug}`}><LocalizedText value={" Plan Financing "} /><ArrowRight aria-hidden="true" />
                  </Link>
                </div>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      <section className="financial-selection">
        <div className="section-title-wrap">
          <h2><LocalizedText value={"All Business Profiles"} /></h2>
          <span className="selection-count">{businesses.length}<LocalizedText value={" supported businesses"} /></span>
        </div>
        <div className="financial-business-grid">
          {businesses.map(item => (
            <article key={item.id} className="financial-business-card">
              <div className="card-top">
                <span className="business-cat-badge"><LocalizedText value={categoryLabels[item.category]} /></span>
              </div>
              <h3>{item.name}</h3>
              <p><LocalizedText value={item.shortDescription} /></p>
              <div className="capital-hint">
                <small><LocalizedText value={"Estimated Capital Range"} /></small>
                <strong>{moneyRange(item.minimumCapital, item.maximumCapital)}</strong>
              </div>
              <div className="card-footer">
                <Link className="button button--outline button--sm" to={`/financial-plan/${item.slug}`}><LocalizedText value={" Plan Financing "} /><ArrowRight aria-hidden="true" />
                </Link>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}

function FinancialCalculator({ businessId }: { businessId: string }) {
  const { text: textUi } = useTextUi()

  const { t } = useUi()
  const requestVersion = useRef(0)
  const [dirty, setDirty] = useState(false)
  const [business, setBusiness] = useState<BusinessDetail | null>(null)
  const [profile, setProfile] = useState<EntrepreneurProfile | null>(null)
  const [feasibility, setFeasibility] = useState<FeasibilityAnalysis | null>(null)
  const [previous, setPrevious] = useState<FinancialAnalysis | null>(null)
  const [result, setResult] = useState<FinancialAnalysis | null>(null)
  const [margin, setMargin] = useState('')
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')
  const [inputError, setInputError] = useState('')

  useEffect(() => {
    let active = true
    void Promise.all([
      businessService.get(businessId),
      profileService.get(),
      feasibilityService.latest(),
      financialService.latest(businessId),
    ])
      .then(([savedBusiness, savedProfile, savedFeasibility, savedFinancial]) => {
        if (!active) return
        setBusiness(savedBusiness)
        setProfile(savedProfile)
        setFeasibility(savedFeasibility)
        setPrevious(savedFinancial)
        setResult(savedFinancial)
        setMargin(savedFinancial?.availableMarginCapital ?? savedProfile?.ownCapital ?? '')
      })
      .catch(reason => {
        if (active) setError(getApiErrorMessage(reason, 'Unable to load the financial calculator.'))
      })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false; requestVersion.current += 1 }
  }, [businessId])

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    const paise = parseINRToPaise(margin)
    if (paise === null || paise <= 0n) {
      setInputError('Enter a valid amount greater than zero with no more than two decimal places.')
      return
    }
    if (paise > 1000000000n) {
      setInputError('Enter an amount within the ₹1 crore prototype limit.')
      return
    }
    if (!business || running) return

    setInputError('')
    setError('')
    setRunning(true)
    setResult(null)
    const version = ++requestVersion.current

    try {
      const linked = feasibility?.results.some(item => item.businessId === business.id)
        ? feasibility.id
        : undefined
      const saved = await financialService.analyze(business.slug, margin, linked)
      if (version !== requestVersion.current) return
      setResult(saved)
      setPrevious(saved)
      setDirty(false)
    } catch (reason) {
      if (version === requestVersion.current) setError(getApiErrorMessage(reason, 'Unable to calculate the financial structure.'))
    } finally {
      if (version === requestVersion.current) setRunning(false)
    }
  }

  if (loading) {
    return (
      <div className="financial-page">
        <div className="financial-loading">
          <LoaderCircle className="spin" /><LocalizedText value={" Loading financial calculator… "} /></div>
      </div>
    )
  }

  if (!business) {
    return (
      <div className="financial-page">
        <div className="financial-error" role="alert">
          <AlertCircle aria-hidden="true" />
          <span><LocalizedText value={error || 'Business profile not found.'} /></span>
        </div>
        <Link className="detail-back" to="/opportunities">
          <ArrowLeft aria-hidden="true" /><LocalizedText value={" Back to Opportunities "} /></Link>
      </div>
    )
  }

  return (
    <div className="financial-page">
      <Link className="detail-back" to="/opportunities">
        <ArrowLeft aria-hidden="true" /><LocalizedText value={" Back to Opportunities "} /></Link>

      <header className="financial-heading">
        <span className="eyebrow"><LocalizedText value={"Exact INR decision support"} /></span>
        <h1><LocalizedText value={"Smart Financial Calculator"} /></h1>
        <p><LocalizedText value={"Convert your available margin capital into an indicative project-cost and financing structure."} /></p>
      </header>

      {/* Business Summary */}
      <section className="financial-business-summary">
        <div className="summary-main">
          <span className="business-cat-badge"><LocalizedText value={categoryLabels[business.category]} /></span>
          <h2>{business.name}</h2>
          <p><LocalizedText value={business.shortDescription} /></p>
        </div>
        <dl className="summary-metrics">
          <div>
            <dt><LocalizedText value={"Typical Setup Cost"} /></dt>
            <dd>{moneyRange(business.estimatedSetupCostMin, business.estimatedSetupCostMax)}</dd>
          </div>
          <div>
            <dt><LocalizedText value={"Working Capital Range"} /></dt>
            <dd>{moneyRange(business.workingCapitalMin, business.workingCapitalMax)}</dd>
          </div>
        </dl>
      </section>

      {/* Statutory & Planning Notice */}
      <div className="financial-notice">
        <ShieldCheck aria-hidden="true" />
        <p><LocalizedText value={" This calculator provides an indicative financing structure for decision support. It does not constitute loan approval, sanction, scheme eligibility, or financial advice. "} /></p>
      </div>

      {/* Input Card & Previous Calculation */}
      <div className="financial-input-layout">
        <section className="financial-input-card">
          <form onSubmit={event => void submit(event)} noValidate>
            <div className="form-group">
              <label htmlFor="margin-capital"><LocalizedText value={"Available Margin Capital"} /></label>
              <div className={inputError ? 'money-input money-input--error' : 'money-input'}>
                <span aria-hidden="true">₹</span>
                <input
                  id="margin-capital"
                  inputMode="decimal"
                  value={margin}
                  disabled={running}
                  onChange={event => {
                    setMargin(event.target.value)
                    setResult(null)
                    setDirty(Boolean(result || previous))
                    if (inputError) setInputError('')
                  }}
                  aria-describedby="margin-help margin-error"
                  aria-invalid={Boolean(inputError)}
                  placeholder={textUi("100000.00")}
                />
              </div>
              <small id="margin-help" className="field-hint"><LocalizedText value={" Enter the amount you can contribute from your own funds. "} /></small>
              {!profile?.ownCapital && profile?.capitalRange && (
                <p className="profile-range-note">
                  <Info aria-hidden="true" /><LocalizedText value={" Profile capital range:"} /><LocalizedText value={' '} />
                  <strong><LocalizedText value={profile.capitalRange.replaceAll('_', ' ').toLowerCase()} /></strong><LocalizedText value={". An exact amount is required and has not been invented. "} /></p>
              )}
              {inputError && (
                <p id="margin-error" className="field-error" role="alert">
                  <AlertCircle aria-hidden="true" /> <LocalizedText value={inputError} />
                </p>
              )}
            </div>

            <Button type="submit" disabled={running}>
              {running ? (
                <>
                  <LoaderCircle className="spin" /><LocalizedText value={" Calculating… "} /></>
              ) : (
                'Calculate Financial Structure'
              )}
            </Button>
          </form>
        </section>

        {previous && (
          <aside className="previous-calculation">
            <div className="prev-head">
              <RotateCcw aria-hidden="true" />
              <h3><LocalizedText value={"Previous Calculation"} /></h3>
            </div>
            <p className="prev-date"><LocalizedDate value={previous.createdAt} /></p>
            <dl className="prev-dl">
              <div>
                <dt><LocalizedText value={"Margin"} /></dt>
                <dd>{formatINR(previous.availableMarginCapital, { fractionDigits: 2 })}</dd>
              </div>
              <div>
                <dt><LocalizedText value={"Project Cost"} /></dt>
                <dd>{formatINR(previous.feasibleProjectCost, { fractionDigits: 2 })}</dd>
              </div>
              <div>
                <dt><LocalizedText value={"Indicative Loan"} /></dt>
                <dd>{formatINR(previous.indicativeLoanAmount, { fractionDigits: 2 })}</dd>
              </div>
            </dl>
            <Button
              variant="outline"
              type="button"
              className="button--sm"
              disabled={running}
              onClick={() => {
                setMargin(previous.availableMarginCapital)
                setResult(previous)
                setDirty(false)
                setError('')
                setInputError('')
              }}
            >
              {t.schemeRouter.saved}
            </Button>
          </aside>
        )}
      </div>

      {error && (
        <div className="financial-error" role="alert">
          <AlertCircle aria-hidden="true" />
          <span><LocalizedText value={error} /></span>
        </div>
      )}

      {/* Results Display */}
      {result ? <FinancialResults key={result.id} analysis={result} /> : !running && (
        <p role="status">{dirty ? t.schemeRouter.stale : t.schemeRouter.empty}</p>
      )}
    </div>
  )
}

function FinancialResults({ analysis }: { analysis: FinancialAnalysis }) {
  const { text: textUi } = useTextUi()

  const alignment = analysis.alignment
  const fundingGapPaise = parseINRToPaise(alignment.fundingGap) ?? 0n
  const capacityAboveMaxPaise = parseINRToPaise(alignment.capacityAboveEstimatedMax) ?? 0n

  return (
    <div className="financial-results" aria-live="polite">
      {/* 4 Core Summary Cards */}
      <section className="financial-result-grid" aria-label={textUi("Calculated financial metrics")}>
        <article className="result-card">
          <small><LocalizedText value={"Available Margin"} /></small>
          <strong>{formatINR(analysis.availableMarginCapital, { fractionDigits: 2 })}</strong>
          <span className="card-subtext"><LocalizedText value={"Your self-funded equity"} /></span>
        </article>
        <article className="result-card result-card--highlight">
          <small><LocalizedText value={"Feasible Project Cost"} /></small>
          <strong>{formatINR(analysis.feasibleProjectCost, { fractionDigits: 2 })}</strong>
          <span className="card-subtext"><LocalizedText value={"Total capital capacity"} /></span>
        </article>
        <article className="result-card result-card--loan">
          <small><LocalizedText value={"Indicative Loan"} /></small>
          <strong>{formatINR(analysis.indicativeLoanAmount, { fractionDigits: 2 })}</strong>
          <span className="card-subtext"><LocalizedText value={"90% of feasible project cost"} /></span>
        </article>
        <article className="result-card">
          <small><LocalizedText value={"Beneficiary Contribution"} /></small>
          <strong>{formatINR(analysis.beneficiaryContribution, { fractionDigits: 2 })}</strong>
          <span className="card-subtext"><LocalizedText value={"10% of feasible project cost"} /></span>
        </article>
      </section>

      {/* 10 / 90 Visual Representation */}
      <section
        className="funding-visual"
        aria-label={textUi("Financing structure: 10 percent beneficiary contribution and 90 percent indicative loan")}
      >
        <div className="funding-visual__header">
          <h2><LocalizedText value={"Financing Structure Breakdown"} /></h2>
          <span className="badge"><LocalizedText value={"10% Margin : 90% Loan"} /></span>
        </div>
        <div className="stacked-bar" role="img" aria-label={textUi("10% Contribution, 90% Loan")}>
          <span className="bar-segment bar-segment--contribution" style={{ width: '10%' }}>
            <b>10%</b>
          </span>
          <span className="bar-segment bar-segment--loan" style={{ width: '90%' }}>
            <b>90%</b>
          </span>
        </div>
        <div className="funding-visual__labels">
          <div className="label-item">
            <span className="indicator indicator--contribution" aria-hidden="true" />
            <div>
              <strong><LocalizedText value={"Your Contribution — 10%"} /></strong>
              <small>{formatINR(analysis.beneficiaryContribution, { fractionDigits: 2 })}</small>
            </div>
          </div>
          <div className="label-item">
            <span className="indicator indicator--loan" aria-hidden="true" />
            <div>
              <strong><LocalizedText value={"Indicative Loan — 90%"} /></strong>
              <small>{formatINR(analysis.indicativeLoanAmount, { fractionDigits: 2 })}</small>
            </div>
          </div>
        </div>
      </section>

      {/* How This Calculation Works (Formula Explanation) */}
      <section className="formula-card">
        <div className="formula-icon" aria-hidden="true">
          <Calculator />
        </div>
        <div className="formula-content">
          <h2><LocalizedText value={"How This Calculation Works"} /></h2>
          <div className="formula-rules">
            <p><LocalizedText value={"• Your contribution = 10% of project cost"} /></p>
            <p><LocalizedText value={"• Project Cost = Available Margin ÷ 10%"} /></p>
            <p><LocalizedText value={"• Indicative Loan = Project Cost × 90%"} /></p>
          </div>
          <div className="formula-applied">
            <code>
              {formatINR(analysis.availableMarginCapital, { fractionDigits: 2 })} ÷ 10% =<LocalizedText value={' '} />
              {formatINR(analysis.feasibleProjectCost, { fractionDigits: 2 })}
            </code>
            <code>
              {formatINR(analysis.feasibleProjectCost, { fractionDigits: 2 })} × 90% =<LocalizedText value={' '} />
              {formatINR(analysis.indicativeLoanAmount, { fractionDigits: 2 })}
            </code>
          </div>
        </div>
      </section>

      {/* Business Cost Alignment */}
      <section className="cost-alignment">
        <header className="cost-alignment__header">
          <div className="header-title">
            <Scale aria-hidden="true" />
            <div>
              <span className="eyebrow"><LocalizedText value={"Prototype planning estimates"} /></span>
              <h2><LocalizedText value={"Business Cost Alignment"} /></h2>
            </div>
          </div>
          <span className={`status-badge status-badge--${alignment.financialReadinessStatus.toLowerCase()}`}>
            <LocalizedText value={alignment.financialReadinessStatus.replaceAll('_', ' ')} />
          </span>
        </header>

        <p className="alignment-explanation"><LocalizedText value={alignment.comparisonExplanation} /></p>

        <div className="alignment-grid">
          <div className="alignment-metric">
            <small><LocalizedText value={"Typical Setup Cost"} /></small>
            <strong>
              {formatINR(analysis.businessCosts.setupCostMin)} – {formatINR(analysis.businessCosts.setupCostMax)}
            </strong>
          </div>
          <div className="alignment-metric">
            <small><LocalizedText value={"Working Capital Range"} /></small>
            <strong>
              {formatINR(analysis.businessCosts.workingCapitalMin)} – {formatINR(analysis.businessCosts.workingCapitalMax)}
            </strong>
          </div>
          <div className="alignment-metric alignment-metric--highlight">
            <small><LocalizedText value={"Your Feasible Project Cost"} /></small>
            <strong>{formatINR(analysis.feasibleProjectCost, { fractionDigits: 2 })}</strong>
          </div>
        </div>

        <p className="working-capital-note"><LocalizedText value={alignment.workingCapitalExplanation} /></p>

        {/* Funding Gap Notice */}
        {fundingGapPaise > 0n && (
          <div className="gap-notice" role="note">
            <ShieldAlert aria-hidden="true" />
            <div>
              <strong><LocalizedText value={"Business Setup Shortfall: "} />{formatINR(alignment.fundingGap, { fractionDigits: 2 })}</strong>
              <p><LocalizedText value={" This compares your calculated project capacity with the minimum estimated setup requirement for this business. "} /></p>
            </div>
          </div>
        )}

        {/* Above-Typical Notice */}
        {capacityAboveMaxPaise > 0n && (
          <div className="above-notice" role="note">
            <TrendingUp aria-hidden="true" />
            <div>
              <strong><LocalizedText value={"Capacity Above Estimated Maximum: "} />{formatINR(alignment.capacityAboveEstimatedMax, { fractionDigits: 2 })}</strong>
              <p><LocalizedText value={" Your calculated project capacity is above the current typical estimate for this business. Consider whether a larger-scale configuration is necessary. "} /></p>
            </div>
          </div>
        )}
      </section>

      {/* Warnings */}
      {analysis.warnings.map(warning => (
        <div className="financial-warning" key={warning.code} role="alert">
          <AlertCircle aria-hidden="true" />
          <div>
            <strong>
              <LocalizedText value={warning.code === 'PROJECT_COST_ABOVE_SUPPORTED_SCHEME_RANGE'
                ? 'Scheme Range Notice'
                : warning.code.replaceAll('_', ' ')} />
            </strong>
            <p>
              <LocalizedText value={warning.code === 'PROJECT_COST_ABOVE_SUPPORTED_SCHEME_RANGE'
                ? 'Calculated project cost exceeds the financing range currently supported by the prototype scheme-routing rules.'
                : warning.message} />
            </p>
          </div>
        </div>
      ))}

      {/* Data Source Notice */}
      <div className="financial-data-notice">
        <CheckCircle2 aria-hidden="true" />
        <p><LocalizedText value={analysis.dataSourceNotice} /></p>
      </div>

      <SchemeEligibilityPanel key={analysis.id} financialAnalysisId={analysis.id} />
    </div>
  )
}
