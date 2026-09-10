import type { AnalysisFinding } from '../../types/businessAnalysis'

export function findingSources(item: AnalysisFinding): string[] {
  if (item.source_type && item.source_type !== 'DYNAMIC') return [item.source_type]
  const sources = item.evidence_ids.map(id => id.startsWith('catalog.baseline') ? 'BUSINESS_BASELINE' : id.startsWith('profile.') ? 'PROFILE' : id.startsWith('financial.') ? 'FINANCIAL' : id.startsWith('market.') ? 'MARKET' : id.startsWith('catalog.') ? 'CATALOG' : 'DYNAMIC')
  return [...new Set(sources.length ? sources : ['DYNAMIC'])]
}
export const sourceLabels: Record<string, string> = {
  BUSINESS_BASELINE: 'Business baseline guidance', PROFILE: 'Profile evidence', MARKET: 'Market evidence',
  FINANCIAL: 'Financial evidence', CATALOG: 'Business catalog guidance', DYNAMIC: 'Analysis evidence',
}
