import axios from 'axios'
import type { EntrepreneurProfile, ExistingBusiness, SelectionItem } from '../types/profile'
import { apiClient } from './apiClient'

type WireSelection = { name: string; other_description?: string | null }
type WireBusiness = {
  business_name: string
  business_category: string
  years_operating: number
  initial_investment: string | number
  monthly_revenue: string | number
  monthly_expenses: string | number
  employee_count: number
  estimated_monthly_customers: number
  major_challenges?: string | null
}
type WireProfile = Record<string, unknown> & {
  proposed_business_id?: string | null
  proposed_business_name?: string | null
  full_name?: string | null
  preferred_language?: string | null
  age_group?: string | null
  education?: string | null
  previous_experience?: string | null
  state?: string | null
  district?: string | null
  taluka?: string | null
  village?: string | null
  pincode?: string | null
  latitude?: string | number | null
  longitude?: string | number | null
  capital_range?: string | null
  own_capital?: string | number | null
  loan_required?: string | number | null
  skills?: WireSelection[] | null
  resources?: WireSelection[] | null
  has_existing_business?: boolean | null
  existing_business?: WireBusiness | null
  onboarding_step?: number | null
  onboarding_completed?: boolean | null
}

const selectionFromWire = (item: WireSelection): SelectionItem => ({
  name: item.name,
  otherDescription: item.other_description ? item.other_description.trim() : undefined,
})

const businessFromWire = (item?: WireBusiness | null): ExistingBusiness | undefined => {
  if (!item) return undefined
  return {
    businessName: item.business_name ?? '',
    businessCategory: item.business_category ?? '',
    yearsOperating: typeof item.years_operating === 'number' ? item.years_operating : 0,
    initialInvestment: item.initial_investment != null ? String(item.initial_investment) : '0',
    monthlyRevenue: item.monthly_revenue != null ? String(item.monthly_revenue) : '0',
    monthlyExpenses: item.monthly_expenses != null ? String(item.monthly_expenses) : '0',
    employeeCount: typeof item.employee_count === 'number' ? item.employee_count : 0,
    estimatedMonthlyCustomers:
      typeof item.estimated_monthly_customers === 'number' ? item.estimated_monthly_customers : 0,
    majorChallenges: item.major_challenges ? item.major_challenges.trim() : '',
  }
}

const fromWire = (w: WireProfile): EntrepreneurProfile => ({
  proposedBusinessId: w.proposed_business_id ?? null,
  proposedBusinessName: w.proposed_business_name ?? null,
  fullName: (w.full_name as string) || '',
  preferredLanguage: (w.preferred_language as EntrepreneurProfile['preferredLanguage']) || 'en',
  ageGroup: (w.age_group as EntrepreneurProfile['ageGroup']) || undefined,
  education: (w.education as EntrepreneurProfile['education']) || undefined,
  previousExperience: (w.previous_experience as EntrepreneurProfile['previousExperience']) || undefined,
  state: (w.state as string) || 'Maharashtra',
  district: (w.district as string) || '',
  taluka: (w.taluka as string) || '',
  village: (w.village as string) || '',
  pincode: (w.pincode as string) || '',
  latitude: w.latitude != null ? String(w.latitude) : undefined,
  longitude: w.longitude != null ? String(w.longitude) : undefined,
  capitalRange: (w.capital_range as EntrepreneurProfile['capitalRange']) || undefined,
  ownCapital: w.own_capital != null ? String(w.own_capital) : '',
  loanRequired: w.loan_required != null ? String(w.loan_required) : '',
  skills: Array.isArray(w.skills) ? w.skills.map(selectionFromWire) : [],
  resources: Array.isArray(w.resources) ? w.resources.map(selectionFromWire) : [],
  hasExistingBusiness: typeof w.has_existing_business === 'boolean' ? w.has_existing_business : undefined,
  existingBusiness: businessFromWire(w.existing_business),
  onboardingStep: typeof w.onboarding_step === 'number' ? w.onboarding_step : 1,
  onboardingCompleted: Boolean(w.onboarding_completed),
})

const businessToWire = (b?: ExistingBusiness): WireBusiness | null => {
  if (!b) return null
  return {
    business_name: b.businessName ? b.businessName.trim() : '',
    business_category: b.businessCategory ? b.businessCategory.trim() : '',
    years_operating: Number(b.yearsOperating) || 0,
    initial_investment: b.initialInvestment !== undefined && b.initialInvestment !== '' ? b.initialInvestment : '0',
    monthly_revenue: b.monthlyRevenue !== undefined && b.monthlyRevenue !== '' ? b.monthlyRevenue : '0',
    monthly_expenses: b.monthlyExpenses !== undefined && b.monthlyExpenses !== '' ? b.monthlyExpenses : '0',
    employee_count: Number(b.employeeCount) || 0,
    estimated_monthly_customers: Number(b.estimatedMonthlyCustomers) || 0,
    major_challenges: b.majorChallenges ? b.majorChallenges.trim() : null,
  }
}

const toWire = (p: EntrepreneurProfile) => ({
  proposed_business_id: p.proposedBusinessId ?? null,
  full_name: p.fullName ? p.fullName.trim() : '',
  preferred_language: p.preferredLanguage || 'en',
  age_group: p.ageGroup || null,
  education: p.education || null,
  previous_experience: p.previousExperience || null,
  state: p.state ? p.state.trim() : null,
  district: p.district ? p.district.trim() : null,
  taluka: p.taluka ? p.taluka.trim() : null,
  village: p.village ? p.village.trim() : null,
  pincode: p.pincode ? p.pincode.trim() : null,
  latitude: p.latitude ? Number(p.latitude) : null,
  longitude: p.longitude ? Number(p.longitude) : null,
  capital_range: p.capitalRange || null,
  own_capital: p.ownCapital !== undefined && p.ownCapital !== '' ? p.ownCapital : null,
  loan_required: p.loanRequired !== undefined && p.loanRequired !== '' ? p.loanRequired : null,
  skills: (p.skills || []).map(i => ({
    name: i.name,
    other_description: i.otherDescription ? i.otherDescription.trim() : null,
  })),
  resources: (p.resources || []).map(i => ({
    name: i.name,
    other_description: i.otherDescription ? i.otherDescription.trim() : null,
  })),
  has_existing_business: typeof p.hasExistingBusiness === 'boolean' ? p.hasExistingBusiness : null,
  existing_business: p.hasExistingBusiness ? businessToWire(p.existingBusiness) : null,
  onboarding_step: p.onboardingStep || 1,
  onboarding_completed: Boolean(p.onboardingCompleted),
})

export const profileService = {
  async setPreferredLanguage(language: 'en' | 'hi' | 'mr'): Promise<void> {
    // The existing API requires the current onboarding step, even for partial updates.
    const current = await profileService.get()
    await apiClient.put('/profile', { preferred_language: language, onboarding_step: current?.onboardingStep ?? 1 })
  },
  async get(): Promise<EntrepreneurProfile | null> {
    try {
      return fromWire((await apiClient.get<WireProfile>('/profile')).data)
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 404) return null
      throw error
    }
  },
  async update(profile: EntrepreneurProfile): Promise<EntrepreneurProfile> {
    return fromWire((await apiClient.put<WireProfile>('/profile', toWire(profile))).data)
  },
}

