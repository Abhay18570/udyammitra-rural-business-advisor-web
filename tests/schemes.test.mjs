import test from 'node:test'
import assert from 'node:assert/strict'
import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import './tsxLoader.mjs'

const { SchemeGuidanceView } = await import('../src/features/schemes/GovernmentSchemesPage.tsx')
const { UiContext } = await import('../src/i18n/uiContextValue.ts')
const { translations } = await import('../src/i18n/translations.ts')
const { localizeText, formatDate } = await import('../src/i18n/localize.ts')
const { formatINR } = await import('../src/utils/inr.ts')

const render = (element, language = 'en') =>
  renderToStaticMarkup(
    React.createElement(
      UiContext.Provider,
      {
        value: {
          language,
          t: translations[language],
          text: v => localizeText(v, language),
          date: v => formatDate(v, language),
        },
      },
      React.createElement(MemoryRouter, null, element)
    )
  )

const canonicalRules = [
  {
    type: 'MICRO_FINANCE',
    displayName: 'Micro Finance',
    projectCostMin: '0.00',
    projectCostMax: '140000.00',
    projectCostMinInclusive: false,
    projectCostMaxInclusive: true,
    maximumLoanAmount: '125000.00',
    annualInterestRatePercent: '6.50',
    tenureMonths: 36,
    moratoriumMonths: 3,
  },
  {
    type: 'TERM_LOAN',
    displayName: 'Term Loan',
    projectCostMin: '140000.00',
    projectCostMax: '5000000.00',
    projectCostMinInclusive: false,
    projectCostMaxInclusive: true,
    maximumLoanAmount: '4500000.00',
    annualInterestRatePercent: '8.00',
    tenureMonths: 84,
    moratoriumMonths: 6,
  },
]

function makeGuidanceFixture({
  source = 'SAVED_FINANCIAL_PLAN',
  projectCost = '500000.00',
  beneficiaryContribution = '50000.00',
  financingRequirement = '450000.00',
  indicativeFinancedPrincipal = '450000.00',
  schemeFinancingGap = '0.00',
  fullyCovered = true,
  additionalContributionRequired = '0.00',
  totalContributionRequired = '50000.00',
  schemeType = 'TERM_LOAN',
  schemeStatus = 'ELIGIBLE',
  businessName = 'Kirana Store',
  setupFundingGap = '0.00',
  notice = null,
} = {}) {
  const scheme = schemeType
    ? canonicalRules.find(r => r.type === schemeType) ?? null
    : null

  const result = schemeType === undefined && schemeStatus === 'NO_DATA'
    ? null
    : {
        financialAnalysisId: source === 'SAVED_FINANCIAL_PLAN' ? 'test-id-123' : null,
        financialAnalysisVersion: source === 'SAVED_FINANCIAL_PLAN' ? 'financial-v1' : null,
        schemeRulesVersion: 'scheme-v1',
        calculationStatus: 'CALCULATED',
        schemeStatus,
        currency: 'INR',
        rounding: 'HALF_UP_TO_PAISE',
        eligibilityBasis: 'PROTOTYPE_FINANCING_RULES',
        verificationRequired: true,
        business: businessName ? { id: 'biz-1', name: businessName, slug: 'kirana-store', category: 'RETAIL' } : null,
        projectCost,
        beneficiaryContribution,
        financingRequirement,
        indicativeFinancedPrincipal: scheme ? indicativeFinancedPrincipal : null,
        schemeFinancingGap: scheme ? schemeFinancingGap : null,
        fullyCovered: scheme ? fullyCovered : null,
        additionalContributionRequired: scheme ? additionalContributionRequired : null,
        totalContributionRequired: scheme ? totalContributionRequired : null,
        scheme,
        repaymentBasis: null,
        eligibilityReasons: scheme
          ? [
              {
                code: `${scheme.type}_PROJECT_TIER`,
                params: { project_cost: projectCost },
                message: `Your project cost of ₹${formatINR(projectCost)} falls in the ${scheme.displayName} tier.`,
              },
            ]
          : [
              {
                code: 'PROJECT_OUT_OF_SUPPORTED_RANGE',
                params: { project_cost: projectCost },
                message: `Your project cost of ₹${formatINR(projectCost)} exceeds the ₹50,00,000.00 financing range supported by this SIH prototype.`,
              },
            ],
        warnings: schemeFinancingGap && Number(schemeFinancingGap) > 0
          ? [
              {
                code: 'SCHEME_LOAN_CAP_GAP',
                params: { gap: schemeFinancingGap },
                message: `Your financing requirement is ₹${formatINR(financingRequirement)}, but the scheme loan cap is ₹${formatINR(scheme.maximumLoanAmount)}, leaving a shortfall of ₹${formatINR(schemeFinancingGap)}.`,
              },
            ]
          : [],
        nextSteps: [
          { code: 'VERIFY_LENDER_TERMS', params: {}, message: 'Verify eligibility and terms with the lender before applying.' },
        ],
        disclaimer: 'This result applies SIH prototype financing rules only. Lender eligibility and terms require verification; this is not loan approval or sanction.',
      }

  return {
    source,
    result,
    rules: canonicalRules,
    schemeRulesVersion: 'scheme-v1',
    fundingSharePercent: '90.0',
    contributionSharePercent: '10.0',
    setupFundingGap,
    sourceObservedAt: '2026-09-09T10:00:00Z',
    notice,
    disclaimer: 'This result applies SIH prototype financing rules only. Lender eligibility and terms require verification; this is not loan approval or sanction.',
  }
}

test('1. both scheme cards render', () => {
  const data = makeGuidanceFixture()
  const html = render(React.createElement(SchemeGuidanceView, { data }))
  assert.match(html, /All Available Schemes/)
  assert.match(html, /Micro Finance/)
  assert.match(html, /Term Loan/)
  assert.match(html, /class="scheme-grid"/)
})

test('2. Micro Finance always visible', () => {
  const data = makeGuidanceFixture({ schemeType: 'TERM_LOAN', projectCost: '500000.00' })
  const html = render(React.createElement(SchemeGuidanceView, { data }))
  assert.match(html, /Micro Finance/)
  assert.match(html, /Up to ₹1\.40 lakh/)
})

test('3. Term Loan always visible', () => {
  const data = makeGuidanceFixture({ schemeType: 'MICRO_FINANCE', projectCost: '100000.00' })
  const html = render(React.createElement(SchemeGuidanceView, { data }))
  assert.match(html, /Term Loan/)
  assert.match(html, /Above ₹1\.40 lakh up to ₹50 lakh/)
})

test('4. recommended scheme highlighted', () => {
  const data = makeGuidanceFixture({ schemeType: 'TERM_LOAN', projectCost: '500000.00' })
  const html = render(React.createElement(SchemeGuidanceView, { data }))
  assert.match(html, /Recommended Scheme/)
  assert.match(html, /scheme-panel--recommended/)
  assert.match(html, /scheme-card--recommended/)
})

test('5. non-recommended scheme remains viewable', () => {
  const data = makeGuidanceFixture({ schemeType: 'TERM_LOAN', projectCost: '500000.00' })
  const html = render(React.createElement(SchemeGuidanceView, { data }))
  assert.match(html, /Micro Finance/)
  assert.match(html, /Not Applicable/)
  assert.match(html, /Your project cost exceeds the ₹1\.40 lakh Micro Finance limit\./)
})

test('6. View Details works for Micro', () => {
  const data = makeGuidanceFixture()
  const html = render(React.createElement(SchemeGuidanceView, { data }))
  assert.match(html, /aria-controls="scheme-detail-MICRO_FINANCE"/)
  assert.match(html, /View Details/)
})

test('7. View Details works for Term', () => {
  const data = makeGuidanceFixture()
  const html = render(React.createElement(SchemeGuidanceView, { data }))
  assert.match(html, /aria-controls="scheme-detail-TERM_LOAN"/)
  assert.match(html, /View Details/)
})

test('8. comparison section renders', () => {
  const data = makeGuidanceFixture()
  const html = render(React.createElement(SchemeGuidanceView, { data }))
  assert.match(html, /Compare Schemes/)
  assert.match(html, /class="scheme-comparison-table"/)
  assert.match(html, /<th[^>]*>Feature<\/th>/)
  assert.match(html, /<th[^>]*>Micro Finance<\/th>/)
  assert.match(html, /<th[^>]*>Term Loan<\/th>/)
})

test('9. correct Micro values', () => {
  const data = makeGuidanceFixture()
  const html = render(React.createElement(SchemeGuidanceView, { data }))
  assert.match(html, /₹1,25,000/)
  assert.match(html, /6\.5/)
  assert.match(html, /36/)
  assert.match(html, /3/)
})

test('10. correct Term values', () => {
  const data = makeGuidanceFixture()
  const html = render(React.createElement(SchemeGuidanceView, { data }))
  assert.match(html, /₹45,00,000/)
  assert.match(html, /8/)
  assert.match(html, /84/)
  assert.match(html, /6/)
})

test('11. current applicability shown', () => {
  const data = makeGuidanceFixture({ schemeType: 'TERM_LOAN', projectCost: '300000.00' })
  const html = render(React.createElement(SchemeGuidanceView, { data }))
  assert.match(html, /Your project cost falls within the Term Loan range\./)
  assert.match(html, /Your project cost exceeds the ₹1\.40 lakh Micro Finance limit\./)
})

test('12. project ₹1,00,000 => Micro recommended', () => {
  const data = makeGuidanceFixture({
    projectCost: '100000.00',
    beneficiaryContribution: '10000.00',
    financingRequirement: '90000.00',
    indicativeFinancedPrincipal: '90000.00',
    schemeFinancingGap: '0.00',
    schemeType: 'MICRO_FINANCE',
    schemeStatus: 'ELIGIBLE',
  })
  const html = render(React.createElement(SchemeGuidanceView, { data }))
  assert.match(html, /Recommended Scheme/)
  assert.match(html, /Micro Finance/)
  assert.match(html, /₹1,00,000/)
  assert.match(html, /₹90,000/)
  assert.match(html, /Eligible/)
})

test('13. project ₹1,40,000 => Micro recommended', () => {
  const data = makeGuidanceFixture({
    projectCost: '140000.00',
    beneficiaryContribution: '14000.00',
    financingRequirement: '126000.00',
    indicativeFinancedPrincipal: '125000.00',
    schemeFinancingGap: '1000.00',
    fullyCovered: false,
    additionalContributionRequired: '1000.00',
    totalContributionRequired: '15000.00',
    schemeType: 'MICRO_FINANCE',
    schemeStatus: 'ELIGIBLE_WITH_GAP',
  })
  const html = render(React.createElement(SchemeGuidanceView, { data }))
  assert.match(html, /Micro Finance/)
  assert.match(html, /₹1,40,000/)
  assert.match(html, /₹1,25,000/)
  assert.match(html, /₹1,000/)
  assert.match(html, /₹15,000/)
  assert.match(html, /Eligible with additional contribution/)
})

test('14. project ₹1,40,001 => Term recommended', () => {
  const data = makeGuidanceFixture({
    projectCost: '140000.10',
    beneficiaryContribution: '14000.01',
    financingRequirement: '126000.09',
    indicativeFinancedPrincipal: '126000.09',
    schemeFinancingGap: '0.00',
    schemeType: 'TERM_LOAN',
    schemeStatus: 'ELIGIBLE',
  })
  const html = render(React.createElement(SchemeGuidanceView, { data }))
  assert.match(html, /Term Loan/)
  assert.match(html, /₹1,40,000\.10/)
  assert.match(html, /Eligible/)
})

test('15. project ₹3,00,000 => Term recommended', () => {
  const data = makeGuidanceFixture({
    projectCost: '300000.00',
    beneficiaryContribution: '30000.00',
    financingRequirement: '270000.00',
    indicativeFinancedPrincipal: '270000.00',
    schemeFinancingGap: '0.00',
    schemeType: 'TERM_LOAN',
    schemeStatus: 'ELIGIBLE',
  })
  const html = render(React.createElement(SchemeGuidanceView, { data }))
  assert.match(html, /Term Loan/)
  assert.match(html, /₹3,00,000/)
  assert.match(html, /₹2,70,000/)
  assert.match(html, /₹0/)
  assert.match(html, /Eligible/)
})

test('16. project ₹50,00,000 => Term recommended', () => {
  const data = makeGuidanceFixture({
    projectCost: '5000000.00',
    beneficiaryContribution: '500000.00',
    financingRequirement: '4500000.00',
    indicativeFinancedPrincipal: '4500000.00',
    schemeFinancingGap: '0.00',
    schemeType: 'TERM_LOAN',
    schemeStatus: 'ELIGIBLE',
  })
  const html = render(React.createElement(SchemeGuidanceView, { data }))
  assert.match(html, /Term Loan/)
  assert.match(html, /₹50,00,000/)
  assert.match(html, /₹45,00,000/)
  assert.match(html, /Eligible/)
})

test('17. project ₹50,00,001 => no recommendation, but both schemes visible', () => {
  const data = makeGuidanceFixture({
    projectCost: '5000000.10',
    beneficiaryContribution: '500000.01',
    financingRequirement: '4500000.09',
    schemeType: null,
    schemeStatus: 'OUT_OF_SUPPORTED_RANGE',
  })
  const html = render(React.createElement(SchemeGuidanceView, { data }))
  assert.match(html, /Outside supported scheme range/)
  assert.match(html, /All Available Schemes/)
  assert.match(html, /Micro Finance/)
  assert.match(html, /Term Loan/)
  assert.match(html, /Compare Schemes/)
})

test('18. funding gap shown where applicable', () => {
  const data = makeGuidanceFixture({
    projectCost: '140000.00',
    beneficiaryContribution: '14000.00',
    financingRequirement: '126000.00',
    indicativeFinancedPrincipal: '125000.00',
    schemeFinancingGap: '1000.00',
    additionalContributionRequired: '1000.00',
    totalContributionRequired: '15000.00',
    schemeType: 'MICRO_FINANCE',
    schemeStatus: 'ELIGIBLE_WITH_GAP',
  })
  const html = render(React.createElement(SchemeGuidanceView, { data }))
  assert.match(html, /Funding Gap/)
  assert.match(html, /Additional Contribution/)
  assert.match(html, /Total Contribution for the Same Project/)
  assert.match(html, /These contributions fund the same project/)
})

test('19. English', () => {
  const data = makeGuidanceFixture({ projectCost: '500000.00', schemeType: 'TERM_LOAN' })
  const html = render(React.createElement(SchemeGuidanceView, { data }), 'en')
  assert.match(html, /Your Financing Position/)
  assert.match(html, /Recommended Scheme/)
  assert.match(html, /All Available Schemes/)
  assert.match(html, /Compare Schemes/)
  assert.match(html, /How This Was Calculated/)
  assert.match(html, /Guidance \/ Next Step/)
  assert.match(html, /Scheme rules used by UdyamMitra/)
})

test('20. Hindi', () => {
  const data = makeGuidanceFixture({ projectCost: '500000.00', schemeType: 'TERM_LOAN' })
  const html = render(React.createElement(SchemeGuidanceView, { data }), 'hi')
  assert.match(html, /आपकी वित्तीय स्थिति/)
  assert.match(html, /सुझाई गई योजना/)
  assert.match(html, /सभी उपलब्ध योजनाएं/)
  assert.match(html, /योजनाओं की तुलना करें/)
  assert.match(html, /यह गणना कैसे हुई/)
  assert.match(html, /मार्गदर्शन \/ अगला कदम/)
  assert.match(html, /UdyamMitra द्वारा उपयोग किए गए योजना नियम/)
})

test('21. Marathi', () => {
  const data = makeGuidanceFixture({ projectCost: '500000.00', schemeType: 'TERM_LOAN' })
  const html = render(React.createElement(SchemeGuidanceView, { data }), 'mr')
  assert.match(html, /तुमची आर्थिक स्थिती/)
  assert.match(html, /सुचवलेली योजना/)
  assert.match(html, /सर्व उपलब्ध योजना/)
  assert.match(html, /योजनांची तुलना करा/)
  assert.match(html, /ही गणना कशी केली/)
  assert.match(html, /मार्गदर्शन \/ पुढील पाऊल/)
  assert.match(html, /UdyamMitra मध्ये वापरलेले योजना नियम/)
})

test('22. responsive component does not depend on fixed desktop width', () => {
  const data = makeGuidanceFixture()
  const html = render(React.createElement(SchemeGuidanceView, { data }))
  assert.match(html, /scheme-grid/)
  assert.match(html, /scheme-comparison-wrap/)
  assert.doesNotMatch(html, /style="[^"]*width:\s*\d{3,}px/)
})

test('23. user is never asked to manually choose scheme', () => {
  const data = makeGuidanceFixture()
  const html = render(React.createElement(SchemeGuidanceView, { data }))
  assert.doesNotMatch(html, /<select/)
  assert.doesNotMatch(html, /<input[^>]*type="radio"/)
  assert.doesNotMatch(html, /<input[^>]*type="number"/)
})

test('24. no EMI schedule added', () => {
  const data = makeGuidanceFixture()
  const html = render(React.createElement(SchemeGuidanceView, { data }))
  assert.doesNotMatch(html, /Monthly EMI/i)
  assert.doesNotMatch(html, /Repayment Schedule/i)
  assert.doesNotMatch(html, /Amortization/i)
  assert.match(html, /Interest Rate/i)
  assert.match(html, /Tenure/i)
  assert.match(html, /Moratorium/i)
})
