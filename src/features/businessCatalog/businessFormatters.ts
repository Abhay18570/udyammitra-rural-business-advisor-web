export const categoryLabels: Record<string, string> = { RETAIL: 'Retail', SERVICES: 'Services', AGRICULTURE: 'Agriculture', FOOD_PROCESSING: 'Food Processing', MANUFACTURING: 'Manufacturing' }
export const typeLabels: Record<string, string> = { SERVICE: 'Service', RETAIL: 'Retail', AGRI_ALLIED: 'Agri-allied', PROCESSING: 'Processing', RENTAL: 'Rental' }
export function formatMoney(value: string): string { return formatINR(value, { fallback: 'Not available' }) }
export const moneyRange = (minimum: string, maximum: string) => `${formatMoney(minimum)} – ${formatMoney(maximum)}`
import { formatINR } from '../../utils/inr'
