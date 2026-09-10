import type { VerificationStatus } from '../../types/governmentScheme'
export const disclaimer = 'Imported scheme information is discovery data and should be verified against current official sources before application.'
export const statusLabels: Record<VerificationStatus, string> = { DATASET_ONLY: 'Dataset Only', OFFICIAL_SOURCE_LINKED: 'Official Source Linked', VERIFIED: 'Verified', STALE: 'Stale' }
