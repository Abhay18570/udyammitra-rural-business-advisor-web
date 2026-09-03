export type FeasibilityLabel = 'LOW' | 'MODERATE' | 'GOOD' | 'STRONG' | 'VERY_STRONG'
export type ComponentCode = 'LOCAL_DEMAND' | 'COMPETITION_OPPORTUNITY' | 'SKILL_MATCH' | 'FINANCIAL_FIT' | 'MARKET_ACCESS' | 'SUPPLY_CHAIN'
export interface ScoreComponent { code: ComponentCode; title: string; score: number; weight: string; weightedContribution: string }
export interface ExplanationItem { code: string; title: string; explanation: string }
export interface GapItem { code: string; severity: 'LOW' | 'MEDIUM' | 'HIGH'; explanation: string }
export interface SkillEvidence { matchedRequiredSkills: string[]; missingRequiredSkills: string[]; matchedPreferredSkills: string[]; skillMatchScore: number }
export interface ResourceEvidence { availableRequiredResources: string[]; missingRequiredResources: string[]; availableOptionalResources: string[]; resourceReadinessScore: number }
export interface FeasibilityResult {
  rank: number; businessId: string; businessSlug: string; businessName: string; businessCategory: string; shortDescription: string
  finalFeasibilityScore: number; feasibilityLabel: FeasibilityLabel; isCurrentBusiness: boolean; components: ScoreComponent[]
  skills: SkillEvidence; resources: ResourceEvidence; capitalFitExplanation: string; financingMayBeRequired: boolean
  strengths: ExplanationItem[]; gaps: GapItem[]; nextActions: string[]; marketThreats: Array<{ code: string; explanation: string }>
}
export interface FeasibilityAnalysis { id: string; createdAt: string; analysisVersion: string; marketAnalysisId: string; marketAnalysisVersion: string; marketDataVersion: string; disclaimer: string; results: FeasibilityResult[]; topMatches: FeasibilityResult[] }
