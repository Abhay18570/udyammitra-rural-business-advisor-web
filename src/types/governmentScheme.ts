export type SchemeLevel = 'CENTRAL' | 'STATE'
export type VerificationStatus = 'DATASET_ONLY' | 'OFFICIAL_SOURCE_LINKED' | 'VERIFIED' | 'STALE'
export type CatalogSort = 'name_asc' | 'name_desc' | 'newest' | 'oldest'
export interface GovernmentSchemeListItem {
  slug: string; scheme_name: string; short_description: string; level: SchemeLevel; state: string | null
  categories: string[]; tags: string[]; verification_status: VerificationStatus; source_type: string
}
export interface GovernmentSchemeListResponse {
  items: GovernmentSchemeListItem[]; total: number; page: number; page_size: number; total_pages: number; disclaimer: string
}
export interface GovernmentSchemeDetail extends Omit<GovernmentSchemeListItem, 'short_description'> {
  details: string; benefits: string; eligibility: string; application_process: string | null; documents_required: string | null
  source_dataset: string; is_active: boolean; created_at: string; updated_at: string; disclaimer: string
}
export interface GovernmentSchemeFilters {
  levels: SchemeLevel[]; states: string[]; categories: string[]; verification_statuses: VerificationStatus[]
}
export interface GovernmentSchemeQuery {
  page: number; page_size: number; sort: CatalogSort; search?: string; level?: SchemeLevel
  state?: string; category?: string; verification_status?: VerificationStatus
}
