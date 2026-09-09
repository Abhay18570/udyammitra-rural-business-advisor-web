import type { NearbyMarketEvidence, NearbyPOI } from './nearbyMarket'
export interface AnalysisEvidence { id: string; value: unknown; source_kind: string; source_ref: string; observed_at: string | null; unit: string | null; limitations: string[] }
export interface AnalysisFinding { id: string; rule_id: string; title: string; explanation: string; importance: string | null; evidence_ids: string[]; finding_ids: string[]; limitations: string[] }
export interface AnalysisThreat { id: string; title: string; description: string; evidence_kind: string; severity: string | null; severity_reason: string | null; likelihood: string | null; mitigation: string; evidence_ids: string[]; coverage_warnings: string[] }
export interface BusinessAnalysis {
  id: string; created_at: string
  business: { id: string; slug: string; name: string; category: string; business_type: string; catalog_hash: string }
  profile_context: { enterprise_stage: string }
  financial_context: { analysis: { id: string; feasible_project_cost: string; available_margin_capital: string }; budget: { consistency_status: string; own_capital: string | null }; scheme: { scheme_financing_gap: string | null } }
  market_context: NearbyMarketEvidence
  swot: Record<string, AnalysisFinding[]>
  local_threats: AnalysisThreat[]
  competition: { selected_radius_km: number; area_km2: number; direct_count: number | null; related_count: number | null; nearest: NearbyPOI | null; average_distance: number | null; mapped_density: number | null; classification: string; provisional: boolean; classification_basis: string; distance_bands: Array<{ lower_km: number; upper_km: number; count: number }>; evidence_ids: string[] }
  pricing: { status: string; strategy: string; items: Array<{ name: string; unit: string; recommended_min: string; recommended_target: string; recommended_max: string; planning_cost_per_unit: string }>; assumptions: unknown[]; missing_assumptions: string[]; demographic_status: string; purchasing_power_status: string; local_price_status: string; warnings: string[]; evidence_ids: string[] }
  evidence: AnalysisEvidence[]
  quality: { rule_versions: Record<string, string>; context_hash: string; warnings: Record<string, string[]>; section_statuses: Record<string, string> }
}
