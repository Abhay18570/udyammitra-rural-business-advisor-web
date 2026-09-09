import { createContext, useContext } from 'react'
import type { Language } from './translations'
import type { translations } from './translations'

export type FontScale = 'small' | 'normal' | 'large'
export type UiContextValue = { text: (value: string | null | undefined) => string; date: (value: string | number | Date) => string; preferenceError: boolean; language: Language; setLanguage: (value: Language) => void; fontScale: FontScale; setFontScale: (value: FontScale) => void; t: (typeof translations)['en'] }
export const UiContext = createContext<UiContextValue | null>(null)
export function useUi() { const value = useContext(UiContext); if (!value) throw new Error('useUi must be used inside UiProvider'); return value }
