import { useEffect, useMemo, useState, type ReactNode } from 'react'
import { translations, type Language } from './translations'
import { UiContext, type FontScale } from './uiContextValue'

export function UiProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>(() => (localStorage.getItem('udyammitra-language') as Language) || 'en')
  const [fontScale, setFontScaleState] = useState<FontScale>(() => (localStorage.getItem('udyammitra-font-scale') as FontScale) || 'normal')
  const setLanguage = (value: Language) => { setLanguageState(value); localStorage.setItem('udyammitra-language', value) }
  const setFontScale = (value: FontScale) => { setFontScaleState(value); localStorage.setItem('udyammitra-font-scale', value) }
  useEffect(() => { document.documentElement.lang = language; document.documentElement.dataset.fontScale = fontScale }, [fontScale, language])
  const value = useMemo(() => ({ language, setLanguage, fontScale, setFontScale, t: translations[language] }), [fontScale, language])
  return <UiContext.Provider value={value}>{children}</UiContext.Provider>
}
