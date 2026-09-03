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
import { type FormEvent, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
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
  return <FinancialCalculator businessId={businessId} />
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
          <LoaderCircle className="spin" /> Loading businesses…
        </div>
      </div>
    )
  }

  return (
    <div className="financial-page">
      <header className="financial-heading">
        <span className="eyebrow">Financial structuring foundation</span>
        <h1>Choose a Business to Plan</h1>
        <p>Select a supported business before entering your available margin capital.</p>
      </header>

      {error && (
        <div className="financial-error" role="alert">
          <AlertCircle aria-hidden="true" />
          <span>{error}</span>
        </div>
      )}

      {feasibility?.topMatches.length ? (
        <section className="financial-selection">
          <div className="section-title-wrap">
            <h2>Top Feasibility Matches</h2>
            <span className="badge badge--success">From your saved feasibility analysis</span>
          </div>
          <div className="financial-business-grid">
            {feasibility.topMatches.map(item => (
              <article key={item.businessId} className="financial-business-card">
                <div className="card-top">
                  <span className="badge badge--primary">Rank {item.rank}</span>
                  <small className="feasibility-tag">{item.feasibilityLabel.replaceAll('_', ' ')}</small>
                </div>
                <h3>{item.businessName}</h3>
                <p>{item.shortDescription}</p>
                <div className="card-footer">
                  <Link className="button button--primary button--sm" to={`/financial-plan/${item.businessSlug}`}>
                    Plan Financing <ArrowRight aria-hidden="true" />
                  </Link>
                </div>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      <section className="financial-selection">
        <div className="section-title-wrap">
          <h2>All Business Profiles</h2>
          <span className="selection-count">{businesses.length} supported businesses</span>
        </div>
        <div className="financial-business-grid">
          {businesses.map(item => (
            <article key={item.id} className="financial-business-card">
              <div className="card-top">
                <span className="business-cat-badge">{categoryLabels[item.category]}</span>
              </div>
              <h3>{item.name}</h3>
              <p>{item.shortDescription}</p>
              <div className="capital-hint">
                <small>Estimated Capital Range</small>
                <strong>{moneyRange(item.minimumCapital, item.maximumCapital)}</strong>
              </div>
              <div className="card-footer">
                <Link className="button button--outline button--sm" to={`/financial-plan/${item.slug}`}>
                  Plan Financing <ArrowRight aria-hidden="true" />
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
    void Promise.all([
      businessService.get(businessId),
      profileService.get(),
      feasibilityService.latest(),
      financialService.latest(businessId),
    ])
      .then(([savedBusiness, savedProfile, savedFeasibility, savedFinancial]) => {
        setBusiness(savedBusiness)
        setProfile(savedProfile)
        setFeasibility(savedFeasibility)
        setPrevious(savedFinancial)
        setMargin(savedProfile?.ownCapital ?? '')
      })
      .catch(reason => setError(getApiErrorMessage(reason, 'Unable to load the financial calculator.')))
      .finally(() => setLoading(false))
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
    if (!business) return

    setInputError('')
    setError('')
    setRunning(true)

    try {
      const linked = feasibility?.results.some(item => item.businessId === business.id)
        ? feasibility.id
        : undefined
      const saved = await financialService.analyze(business.slug, margin, linked)
      setResult(saved)
      setPrevious(saved)
    } catch (reason) {
      setError(getApiErrorMessage(reason, 'Unable to calculate the financial structure.'))
    } finally {
      setRunning(false)
    }
  }

  if (loading) {
    return (
      <div className="financial-page">
        <div className="financial-loading">
          <LoaderCircle className="spin" /> Loading financial calculator…
        </div>
      </div>
    )
  }

  if (!business) {
    return (
      <div className="financial-page">
        <div className="financial-error" role="alert">
          <AlertCircle aria-hidden="true" />
          <span>{error || 'Business profile not found.'}</span>
        </div>
        <Link className="detail-back" to="/opportunities">
          <ArrowLeft aria-hidden="true" /> Back to Opportunities
        </Link>
      </div>
    )
  }

  return (
    <div className="financial-page">
      <Link className="detail-back" to="/opportunities">
        <ArrowLeft aria-hidden="true" /> Back to Opportunities
      </Link>

      <header className="financial-heading">
        <span className="eyebrow">Exact INR decision support</span>
        <h1>Smart Financial Calculator</h1>
        <p>Convert your available margin capital into an indicative project-cost and financing structure.</p>
      </header>

      {/* Business Summary */}
      <section className="financial-business-summary">
        <div className="summary-main">
          <span className="business-cat-badge">{categoryLabels[business.category]}</span>
          <h2>{business.name}</h2>
          <p>{business.shortDescription}</p>
        </div>
        <dl className="summary-metrics">
          <div>
            <dt>Typical Setup Cost</dt>
            <dd>{moneyRange(business.estimatedSetupCostMin, business.estimatedSetupCostMax)}</dd>
          </div>
          <div>
            <dt>Working Capital Range</dt>
            <dd>{moneyRange(business.workingCapitalMin, business.workingCapitalMax)}</dd>
          </div>
        </dl>
      </section>

      {/* Statutory & Planning Notice */}
      <div className="financial-notice">
        <ShieldCheck aria-hidden="true" />
        <p>
          This calculator provides an indicative financing structure for decision support. It does not constitute
          loan approval, sanction, scheme eligibility, or financial advice.
        </p>
      </div>

      {/* Input Card & Previous Calculation */}
      <div className="financial-input-layout">
        <section className="financial-input-card">
          <form onSubmit={event => void submit(event)} noValidate>
            <div className="form-group">
              <label htmlFor="margin-capital">Available Margin Capital</label>
              <div className={inputError ? 'money-input money-input--error' : 'money-input'}>
                <span aria-hidden="true">₹</span>
                <input
                  id="margin-capital"
                  inputMode="decimal"
                  value={margin}
                  onChange={event => {
                    setMargin(event.target.value)
                    if (inputError) setInputError('')
                  }}
                  aria-describedby="margin-help margin-error"
                  aria-invalid={Boolean(inputError)}
                  placeholder="100000.00"
                />
              </div>
              <small id="margin-help" className="field-hint">
                Enter the amount you can contribute from your own funds.
              </small>
              {!profile?.ownCapital && profile?.capitalRange && (
                <p className="profile-range-note">
                  <Info aria-hidden="true" /> Profile capital range:{' '}
                  <strong>{profile.capitalRange.replaceAll('_', ' ').toLowerCase()}</strong>. An exact amount is
                  required and has not been invented.
                </p>
              )}
              {inputError && (
                <p id="margin-error" className="field-error" role="alert">
                  <AlertCircle aria-hidden="true" /> {inputError}
                </p>
              )}
            </div>

            <Button type="submit" disabled={running}>
              {running ? (
                <>
                  <LoaderCircle className="spin" /> Calculating…
                </>
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
              <h3>Previous Calculation</h3>
            </div>
            <p className="prev-date">{new Date(previous.createdAt).toLocaleString('en-IN')}</p>
            <dl className="prev-dl">
              <div>
                <dt>Margin</dt>
                <dd>{formatINR(previous.availableMarginCapital, { fractionDigits: 2 })}</dd>
              </div>
              <div>
                <dt>Project Cost</dt>
                <dd>{formatINR(previous.feasibleProjectCost, { fractionDigits: 2 })}</dd>
              </div>
              <div>
                <dt>Indicative Loan</dt>
                <dd>{formatINR(previous.indicativeLoanAmount, { fractionDigits: 2 })}</dd>
              </div>
            </dl>
            <Button
              variant="outline"
              type="button"
              className="button--sm"
              onClick={() => {
                setMargin(previous.availableMarginCapital)
                setInputError('')
              }}
            >
              Use & Recalculate
            </Button>
          </aside>
        )}
      </div>

      {error && (
        <div className="financial-error" role="alert">
          <AlertCircle aria-hidden="true" />
          <span>{error}</span>
        </div>
      )}

      {/* Results Display */}
      {result && <FinancialResults analysis={result} />}
    </div>
  )
}

function FinancialResults({ analysis }: { analysis: FinancialAnalysis }) {
  const alignment = analysis.alignment
  const fundingGapPaise = parseINRToPaise(alignment.fundingGap) ?? 0n
  const capacityAboveMaxPaise = parseINRToPaise(alignment.capacityAboveEstimatedMax) ?? 0n

  return (
    <div className="financial-results" aria-live="polite">
      {/* 4 Core Summary Cards */}
      <section className="financial-result-grid" aria-label="Calculated financial metrics">
        <article className="result-card">
          <small>Available Margin</small>
          <strong>{formatINR(analysis.availableMarginCapital, { fractionDigits: 2 })}</strong>
          <span className="card-subtext">Your self-funded equity</span>
        </article>
        <article className="result-card result-card--highlight">
          <small>Feasible Project Cost</small>
          <strong>{formatINR(analysis.feasibleProjectCost, { fractionDigits: 2 })}</strong>
          <span className="card-subtext">Total capital capacity</span>
        </article>
        <article className="result-card result-card--loan">
          <small>Indicative Loan</small>
          <strong>{formatINR(analysis.indicativeLoanAmount, { fractionDigits: 2 })}</strong>
          <span className="card-subtext">90% of feasible project cost</span>
        </article>
        <article className="result-card">
          <small>Beneficiary Contribution</small>
          <strong>{formatINR(analysis.beneficiaryContribution, { fractionDigits: 2 })}</strong>
          <span className="card-subtext">10% of feasible project cost</span>
        </article>
      </section>

      {/* 10 / 90 Visual Representation */}
      <section
        className="funding-visual"
        aria-label="Financing structure: 10 percent beneficiary contribution and 90 percent indicative loan"
      >
        <div className="funding-visual__header">
          <h2>Financing Structure Breakdown</h2>
          <span className="badge">10% Margin : 90% Loan</span>
        </div>
        <div className="stacked-bar" role="img" aria-label="10% Contribution, 90% Loan">
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
              <strong>Your Contribution — 10%</strong>
              <small>{formatINR(analysis.beneficiaryContribution, { fractionDigits: 2 })}</small>
            </div>
          </div>
          <div className="label-item">
            <span className="indicator indicator--loan" aria-hidden="true" />
            <div>
              <strong>Indicative Loan — 90%</strong>
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
          <h2>How This Calculation Works</h2>
          <div className="formula-rules">
            <p>• Your contribution = 10% of project cost</p>
            <p>• Project Cost = Available Margin ÷ 10%</p>
            <p>• Indicative Loan = Project Cost × 90%</p>
          </div>
          <div className="formula-applied">
            <code>
              {formatINR(analysis.availableMarginCapital, { fractionDigits: 2 })} ÷ 10% ={' '}
              {formatINR(analysis.feasibleProjectCost, { fractionDigits: 2 })}
            </code>
            <code>
              {formatINR(analysis.feasibleProjectCost, { fractionDigits: 2 })} × 90% ={' '}
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
              <span className="eyebrow">Prototype planning estimates</span>
              <h2>Business Cost Alignment</h2>
            </div>
          </div>
          <span className={`status-badge status-badge--${alignment.financialReadinessStatus.toLowerCase()}`}>
            {alignment.financialReadinessStatus.replaceAll('_', ' ')}
          </span>
        </header>

        <p className="alignment-explanation">{alignment.comparisonExplanation}</p>

        <div className="alignment-grid">
          <div className="alignment-metric">
            <small>Typical Setup Cost</small>
            <strong>
              {formatINR(analysis.businessCosts.setupCostMin)} – {formatINR(analysis.businessCosts.setupCostMax)}
            </strong>
          </div>
          <div className="alignment-metric">
            <small>Working Capital Range</small>
            <strong>
              {formatINR(analysis.businessCosts.workingCapitalMin)} – {formatINR(analysis.businessCosts.workingCapitalMax)}
            </strong>
          </div>
          <div className="alignment-metric alignment-metric--highlight">
            <small>Your Feasible Project Cost</small>
            <strong>{formatINR(analysis.feasibleProjectCost, { fractionDigits: 2 })}</strong>
          </div>
        </div>

        <p className="working-capital-note">{alignment.workingCapitalExplanation}</p>

        {/* Funding Gap Notice */}
        {fundingGapPaise > 0n && (
          <div className="gap-notice" role="note">
            <ShieldAlert aria-hidden="true" />
            <div>
              <strong>Estimated Funding Gap: {formatINR(alignment.fundingGap, { fractionDigits: 2 })}</strong>
              <p>
                This compares your calculated project capacity with the minimum estimated setup requirement for this
                business.
              </p>
            </div>
          </div>
        )}

        {/* Above-Typical Notice */}
        {capacityAboveMaxPaise > 0n && (
          <div className="above-notice" role="note">
            <TrendingUp aria-hidden="true" />
            <div>
              <strong>Capacity Above Estimated Maximum: {formatINR(alignment.capacityAboveEstimatedMax, { fractionDigits: 2 })}</strong>
              <p>
                Your calculated project capacity is above the current typical estimate for this business. Consider
                whether a larger-scale configuration is necessary.
              </p>
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
              {warning.code === 'PROJECT_COST_ABOVE_SUPPORTED_SCHEME_RANGE'
                ? 'Scheme Range Notice'
                : warning.code.replaceAll('_', ' ')}
            </strong>
            <p>
              {warning.code === 'PROJECT_COST_ABOVE_SUPPORTED_SCHEME_RANGE'
                ? 'Calculated project cost exceeds the financing range currently supported by the prototype scheme-routing rules.'
                : warning.message}
            </p>
          </div>
        </div>
      ))}

      {/* Data Source Notice */}
      <div className="financial-data-notice">
        <CheckCircle2 aria-hidden="true" />
        <p>{analysis.dataSourceNotice}</p>
      </div>

      {/* Next Step Panel */}
      <section className="financial-next">
        <div className="next-copy">
          <span className="eyebrow">Next stage</span>
          <h2>Next: Check Financing Scheme</h2>
          <p>{analysis.nextStep}</p>
        </div>
        <div className="next-action">
          <button className="button button--secondary" type="button" disabled>
            Scheme Routing Coming Next
          </button>
        </div>
      </section>
    </div>
  )
}
