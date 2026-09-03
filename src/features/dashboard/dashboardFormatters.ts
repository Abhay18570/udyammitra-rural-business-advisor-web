import type { EntrepreneurProfile, SelectionItem } from '../../types/profile'
import { formatINR } from '../../utils/inr'

export const capitalLabels: Record<string, string> = {
  UP_TO_50000: 'Up to ₹50,000',
  RANGE_50000_TO_100000: '₹50,000–₹1 lakh',
  RANGE_100000_TO_250000: '₹1–2.5 lakh',
  RANGE_250000_TO_500000: '₹2.5–5 lakh',
  RANGE_500000_TO_1000000: '₹5–10 lakh',
  ABOVE_1000000: 'Above ₹10 lakh',
}

export function capitalRange(profile: EntrepreneurProfile): string {
  return profile.capitalRange ? capitalLabels[profile.capitalRange] : 'Not provided'
}

export function formatCurrency(value?: string): string {
  if (value === undefined || value === '') return 'Not provided'
  return formatINR(value, { fractionDigits: 2, fallback: 'Not provided' })
}

export function selectionLabel(item: SelectionItem): string {
  return item.name === 'Other' ? item.otherDescription || 'Other' : item.name
}

export function locationLabel(profile: EntrepreneurProfile): string {
  return [profile.village, profile.taluka, profile.district].filter(Boolean).join(', ') || 'Location not provided'
}
