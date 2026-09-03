import type { PreferredLanguage } from './auth'
import type { capitalRanges } from './analysis'

export type AgeGroup = 'AGE_18_25' | 'AGE_26_35' | 'AGE_36_45' | 'AGE_46_60' | 'AGE_60_PLUS'
export type EducationLevel = 'NO_FORMAL' | 'UP_TO_10TH' | 'TWELFTH' | 'ITI_VOCATIONAL' | 'DIPLOMA' | 'GRADUATE' | 'POSTGRADUATE' | 'OTHER'
export type ExperienceLevel = 'NONE' | 'LESS_THAN_1_YEAR' | 'ONE_TO_THREE_YEARS' | 'THREE_TO_FIVE_YEARS' | 'FIVE_PLUS_YEARS'
export type CapitalRange = (typeof capitalRanges)[number]
export interface SelectionItem { name: string; otherDescription?: string }
export interface ExistingBusiness { businessName: string; businessCategory: string; yearsOperating: number; initialInvestment: string; monthlyRevenue: string; monthlyExpenses: string; employeeCount: number; estimatedMonthlyCustomers: number; majorChallenges?: string }
export interface EntrepreneurProfile { fullName: string; preferredLanguage: PreferredLanguage; ageGroup?: AgeGroup; education?: EducationLevel; previousExperience?: ExperienceLevel; state?: string; district?: string; taluka?: string; village?: string; pincode?: string; latitude?: string; longitude?: string; capitalRange?: CapitalRange; ownCapital?: string; loanRequired?: string; skills: SelectionItem[]; resources: SelectionItem[]; hasExistingBusiness?: boolean; existingBusiness?: ExistingBusiness; onboardingStep: number; onboardingCompleted: boolean }
