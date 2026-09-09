import axios from 'axios'
import { runtimeMessages } from '../i18n/runtimeMessages'
const knownErrors: Record<string, { en: string }> = runtimeMessages.errors

function detailMessage(detail: unknown): string | undefined {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    const messages = detail.map(detailMessage).filter((item): item is string => Boolean(item))
    return messages.length ? messages.join(' ') : undefined
  }
  if (detail && typeof detail === 'object') {
    if ('loc' in detail && Array.isArray(detail.loc)) {
      if (detail.loc.includes('business_query')) return 'Enter a business idea with 2–200 characters.'
      if (detail.loc.includes('radius_km')) return 'Choose a whole-number radius from 1 to 10 km.'
    }
    if ('code' in detail && typeof detail.code === 'string') {
      const known = knownErrors[detail.code.toLowerCase()]
      if (known) return known.en
    }
    if ('message' in detail && typeof detail.message === 'string') return detail.message
    if ('msg' in detail && typeof detail.msg === 'string') return detail.msg
  }
  return undefined
}

export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError<{ detail?: unknown }>(error)) {
    return detailMessage(error.response?.data?.detail)
      ?? (error.code === 'ERR_NETWORK' ? 'Unable to reach the service. Please confirm the backend is running.' : fallback)
  }
  return fallback
}
