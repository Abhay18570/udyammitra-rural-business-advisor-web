import type { CalculationStatus, CurrencyCode, MoneyRounding, SchemeStatus, SchemeType } from './analysis'
import type { FinancialBusiness } from './financial'

export interface SchemeExplanation {
  code: string
  params: Record<string, string>
  message: string
}

export interface SchemeMetadata {
  type: SchemeType
  displayName: string
  projectCostMin: string
  projectCostMax: string
  projectCostMinInclusive: boolean
  projectCostMaxInclusive: boolean
  maximumLoanAmount: string
  annualInterestRatePercent: string
  tenureMonths: number
  moratoriumMonths: number
}

export interface SchemeAnalysis {
  financialAnalysisId: string
  financialAnalysisVersion: string
  schemeRulesVersion: string
  calculationStatus: CalculationStatus
  schemeStatus: SchemeStatus
  currency: CurrencyCode
  rounding: MoneyRounding
  eligibilityBasis: 'PROTOTYPE_FINANCING_RULES'
  verificationRequired: true
  business: FinancialBusiness
  projectCost: string
  beneficiaryContribution: string
  financingRequirement: string
  indicativeFinancedPrincipal: string | null
  schemeFinancingGap: string | null
  fullyCovered: boolean | null
  additionalContributionRequired: string | null
  totalContributionRequired: string | null
  scheme: SchemeMetadata | null
  repaymentBasis: null
  eligibilityReasons: SchemeExplanation[]
  warnings: SchemeExplanation[]
  nextSteps: SchemeExplanation[]
  disclaimer: string
}

export interface SchemeGuidance {
  source: 'SAVED_FINANCIAL_PLAN' | 'PROFILE_ILLUSTRATION' | 'FINANCIAL_PLAN_REQUIRED'
  result: (Omit<SchemeAnalysis, 'financialAnalysisId' | 'financialAnalysisVersion' | 'business'> & {
    financialAnalysisId: string | null
    financialAnalysisVersion: string | null
    business: FinancialBusiness | null
  }) | null
  rules: SchemeMetadata[]
  schemeRulesVersion: string
  fundingSharePercent: string
  contributionSharePercent: string
  setupFundingGap: string | null
  sourceObservedAt: string | null
  notice: 'CONTRIBUTION_UNUSABLE' | null
  disclaimer: string
}
