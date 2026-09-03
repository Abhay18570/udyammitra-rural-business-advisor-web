export type CostCoverageStatus = 'BELOW_TYPICAL_RANGE' | 'WITHIN_TYPICAL_RANGE' | 'ABOVE_TYPICAL_RANGE'

export type FinancialReadinessStatus =
  | 'INSUFFICIENT_CAPITAL_STRUCTURE'
  | 'PARTIALLY_ALIGNED'
  | 'ALIGNED'
  | 'ABOVE_TYPICAL_REQUIREMENT'

export interface FinancialBusiness {
  id: string
  slug: string
  name: string
  category: string
  shortDescription: string
}

export interface BusinessCostSnapshot {
  minimumCapital: string
  maximumCapital: string
  setupCostMin: string
  setupCostMax: string
  estimatedSetupCostMin?: string
  estimatedSetupCostMax?: string
  workingCapitalMin: string
  workingCapitalMax: string
}

export interface BusinessCostAlignment {
  setupCostCoverageStatus: CostCoverageStatus
  financialReadinessStatus: FinancialReadinessStatus
  fundingGap: string
  capacityAboveEstimatedMax: string
  comparisonExplanation: string
  workingCapitalExplanation: string
}

export interface FinancialWarning {
  code: string
  message: string
}

export interface FinancialAnalysis {
  id: string
  createdAt: string
  analysisVersion: string
  feasibilityAnalysisId?: string
  business: FinancialBusiness
  availableMarginCapital: string
  beneficiaryContribution: string
  beneficiaryContributionPercentage?: string
  feasibleProjectCost: string
  indicativeLoanAmount: string
  indicativeLoanPercentage?: string
  businessCosts: BusinessCostSnapshot
  alignment: BusinessCostAlignment
  warnings: FinancialWarning[]
  disclaimer: string
  dataSourceNotice: string
  nextStep: string
}
