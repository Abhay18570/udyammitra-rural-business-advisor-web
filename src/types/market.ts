import type { BusinessCategory } from './business'

export interface MarketLocation { id: string; slug: string; name: string; village: string; taluka: string; district: string; state: string; pincode?: string; latitude: number; longitude: number; isDemo: boolean }
export interface MarketLocationsResponse { locations: MarketLocation[]; resolvedLocationSlug?: string; resolutionStatus: 'resolved_demo_location' | 'unsupported_demo_location'; dataVersion: string; disclaimer: string }
export interface DistributionChannel { type: string; name: string; distanceKm: number }
export interface LocalizedThreat { code: string; explanation: string }
export interface NearbyCompetitor { name: string; category: BusinessCategory; distanceKm: number }
export interface MarketMapPoint { kind: 'BUSINESS' | 'INSTITUTION' | 'AMENITY'; name: string; subtype: string; latitude: number; longitude: number; distanceKm: number }
export interface BusinessMarketResult {
  businessId: string; businessSlug: string; businessName: string; businessCategory: BusinessCategory
  competitors02Km: number; competitors25Km: number; competitors510Km: number
  competitorsWithin2Km: number; competitorsWithin5Km: number; competitorsWithin10Km: number; competitorsWithinSelectedRadius: number
  nearestCompetitorKm?: number; competitionIntensity: number; competitionLabel: string; competitionOpportunityScore: number
  demandScore: number; demandLabel: string; marketReachScore: number; marketAccessScore: number; supplyChainScore: number
  distributionChannels: DistributionChannel[]; localizedThreats: LocalizedThreat[]; evidence: string[]; nearbyCompetitors: NearbyCompetitor[]; marketOpportunitySignal: number
}
export interface MarketSummary { location: string; radiusKm: number; businessPointsConsidered: number; institutionsConsidered: number; amenitiesConsidered: number; lowerCompetitionCategories: string[]; higherDemandCategories: string[]; strongMarketAccessCategories: string[] }
export interface MarketAnalysis { id: string; createdAt: string; analysisVersion: string; dataVersion: string; isDemo: boolean; disclaimer: string; locationSource: 'profile' | 'demo_override'; selectedLocation: MarketLocation; radiusKm: 5 | 10; summary: MarketSummary; businesses: BusinessMarketResult[]; mapPoints: MarketMapPoint[] }
