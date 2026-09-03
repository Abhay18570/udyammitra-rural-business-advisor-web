import type { BusinessCategory } from './business'

export const capitalRanges = ['UP_TO_50000', 'RANGE_50000_TO_100000', 'RANGE_100000_TO_250000', 'RANGE_250000_TO_500000', 'RANGE_500000_TO_1000000', 'ABOVE_1000000'] as const
export const analysisRadiiKm = [5, 10] as const
export const enterpriseStages = ['NEW', 'EXISTING'] as const
export const schemeStatuses = ['ELIGIBLE', 'INELIGIBLE', 'VERIFICATION_REQUIRED'] as const
export const calculationStatuses = ['NOT_CALCULATED', 'CALCULATED', 'UNAVAILABLE'] as const

export type AnalysisRadiusKm = (typeof analysisRadiiKm)[number]
export type EnterpriseStage = (typeof enterpriseStages)[number]
export type SchemeStatus = (typeof schemeStatuses)[number]
export type CalculationStatus = (typeof calculationStatuses)[number]
export type CurrencyCode = 'INR'
export type MoneyRounding = 'HALF_UP_TO_PAISE'

/** Contract for a future analysis request. Monetary values cross the API as decimal strings. */
export interface AnalysisInput {
  location: { state: string; district: string; block: string; village: string; pincode: string; latitude?: string; longitude?: string }
  availableMarginCapital: string
  proposedBusinessId: string
  proposedBusinessCategory: BusinessCategory
  radiusKm: AnalysisRadiusKm
  enterpriseStage: EnterpriseStage
  currency: CurrencyCode
}

/** Vocabulary reserved for future deterministic scheme/calculation results. */
export interface FinancialResultContract {
  calculationStatus: CalculationStatus
  schemeStatus: SchemeStatus
  currency: CurrencyCode
  rounding: MoneyRounding
  feasibleProjectCost?: string
  maximumLoanAmount?: string
  beneficiaryContribution?: string
  fundingGap?: string
}
