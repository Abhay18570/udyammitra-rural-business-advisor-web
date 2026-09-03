export type BusinessCategory = 'RETAIL' | 'SERVICES' | 'AGRICULTURE' | 'FOOD_PROCESSING' | 'MANUFACTURING'
export type BusinessType = 'SERVICE' | 'RETAIL' | 'AGRI_ALLIED' | 'PROCESSING' | 'RENTAL'

export interface BusinessListItem {
  id: string
  slug: string
  name: string
  category: BusinessCategory
  businessType: BusinessType
  shortDescription: string
  minimumCapital: string
  maximumCapital: string
  isActive: boolean
}

export interface BusinessDetail extends BusinessListItem {
  detailedDescription: string
  estimatedSetupCostMin: string
  estimatedSetupCostMax: string
  workingCapitalMin: string
  workingCapitalMax: string
  requiredSkills: string[]
  preferredSkills: string[]
  requiredResources: string[]
  optionalResources: string[]
  equipment: string[]
  customerSegments: string[]
  marketDrivers: string[]
  competitionFactors: string[]
  supplyChainFactors: string[]
  majorRisks: string[]
  requiredRegistrations: string[]
  operatingRequirements: string[]
}

export interface BusinessFilters { category?: BusinessCategory; businessType?: BusinessType; search?: string }
