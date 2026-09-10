import { landingMessages as m } from '../i18n/landingMessages'
import type { Message } from '../i18n/messages'

export interface HomeAlert {
  id: string
  message: Message
}

/**
 * Prototype informational advisory alerts.
 *
 * IMPORTANT: These default alerts are prototype informational notices.
 * They do NOT contain fake deadlines, sanctioned amounts, or official orders.
 *
 * FUTURE-READY NOTE:
 * In a future phase, this default client-side array can easily be replaced
 * or extended by an API response from e.g. GET /api/v1/public/announcements.
 */
export const defaultHomeAlerts: HomeAlert[] = [
  { id: 'alert-1', message: m.homeAlert1 },
  { id: 'alert-2', message: m.homeAlert2 },
  { id: 'alert-3', message: m.homeAlert3 },
  { id: 'alert-4', message: m.homeAlert4 },
  { id: 'alert-5', message: m.homeAlert5 },
  { id: 'alert-6', message: m.homeAlert6 },
]
