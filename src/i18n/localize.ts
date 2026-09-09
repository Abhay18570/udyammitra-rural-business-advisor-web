import { landingMessages } from './landingMessages'
import { runtimeMessages } from './runtimeMessages'
import { enumMessages } from './statusMessages'
import { messages } from './messages'
import { translations, type Language } from './translations'

export const supportedLanguages = ['en', 'hi', 'mr'] as const
export function isLanguage(value: unknown): value is Language { return supportedLanguages.includes(value as Language) }
const normalize = (value: string) => value.trim().replace(/\s+/g, ' ')
const lookup = new Map<string, Record<Language, string>>()
for (const group of Object.values({ landing: landingMessages, ...messages, ...Object.fromEntries(Object.entries(runtimeMessages).map(([key, value]) => [`runtime_${key}`, value])) })) for (const message of Object.values(group)) {
  lookup.set(normalize(message.en), message)
  lookup.set(normalize(message.en).toLowerCase(), message)
}
function addExisting(en: unknown, hi: unknown, mr: unknown) {
  if (typeof en === 'string' && typeof hi === 'string' && typeof mr === 'string') {
    const row = { en, hi, mr }
    lookup.set(normalize(en), row)
    lookup.set(normalize(en).toLowerCase(), row)
  } else if (en && hi && mr && typeof en === 'object' && typeof hi === 'object' && typeof mr === 'object') {
    for (const key of Object.keys(en)) addExisting((en as Record<string, unknown>)[key], (hi as Record<string, unknown>)[key], (mr as Record<string, unknown>)[key])
  }
}
addExisting(translations.en, translations.hi, translations.mr)
for (const [key, row] of Object.entries(enumMessages)) { lookup.set(key, row); lookup.set(key.replaceAll('_', ' ').toLowerCase(), row) }
const patterns: Array<{ regex: RegExp; row: Record<Language, string>; indexes: string[] }> = []
for (const row of new Set(lookup.values())) {
  for (const content of Object.values(row)) {
    lookup.set(normalize(content), row)
    const indexes: string[] = []
    if (!/\{\d+\}/.test(content)) continue
    const escaped = normalize(content).split(/(\{\d+\})/).map(part => {
      if (/^\{\d+\}$/.test(part)) { indexes.push(part.slice(1, -1)); return '(.*?)' }
      return part.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    }).join('')
    patterns.push({ regex: new RegExp('^' + escaped + '$'), row, indexes })
  }
}
/** For UI text and known backend messages only; never pass user or provider names. */
export function localizeText(value: string | undefined | null, language: Language): string {
  if (!value) return value ?? ''
  const key = normalize(value)
  const row = lookup.get(key) ?? lookup.get(key.toLowerCase())
  if (row) return value.replace(value.trim(), row[language])
  const enumLabel = key.replaceAll('_', ' ').toLowerCase()
  const enumRow = lookup.get(enumLabel)
  if (enumRow) return enumRow[language]
  for (const pattern of patterns) {
    const match = pattern.regex.exec(key)
    if (match) {
      const values = Object.fromEntries(pattern.indexes.map((index, i) => [index, match[i + 1]]))
      return pattern.row[language].replace(/\{(\d+)\}/g, (_, index: string) => values[index])
    }
  }
  return value
}
export function readLanguage(storage?: Pick<Storage, 'getItem'>): Language {
  try { const value = storage?.getItem('udyammitra-language'); return isLanguage(value) ? value : 'en' } catch { return 'en' }
}
export function saveLanguage(language: Language, storage?: Pick<Storage, 'setItem'>) {
  try { storage?.setItem('udyammitra-language', language) } catch { /* Storage may be disabled. */ }
}
export function formatDate(value: string | number | Date, language: Language) {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '—' : new Intl.DateTimeFormat(`${language}-IN-u-nu-latn`, { dateStyle: 'medium', timeStyle: 'short' }).format(date)
}

/** A late profile response may only initialize presentation state, never undo a choice. */
export function canApplySavedLanguage(cancelled: boolean, requestedRevision: number, currentRevision: number, requestedOwner: string, currentOwner?: string): boolean {
  return !cancelled && requestedRevision === currentRevision && requestedOwner === currentOwner
}
