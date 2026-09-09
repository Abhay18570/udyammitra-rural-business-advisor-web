import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import { translations, type Language } from './translations'
import { UiContext, type FontScale } from './uiContextValue'
import { canApplySavedLanguage, formatDate, isLanguage, localizeText, readLanguage, saveLanguage } from './localize'
import { useAuth } from '../context/authContextValue'
import { profileService } from '../services/profileService'

export function UiProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  const [language, setLanguageState] = useState<Language>(() => readLanguage(typeof localStorage === 'undefined' ? undefined : localStorage))
  const [fontScale, setFontScaleState] = useState<FontScale>(() => { try { const saved = localStorage.getItem('udyammitra-font-scale'); return saved === 'small' || saved === 'large' ? saved : 'normal' } catch { return 'normal' } })
  const [preferenceError, setPreferenceError] = useState(false)
  const choice = useRef(0)
  const account = useRef(user)
  useEffect(() => { account.current = user }, [user])
  const saves = useRef(Promise.resolve())
  const setLanguage = useCallback((value: Language) => {
    if (!isLanguage(value)) return
    choice.current++
    setLanguageState(value)
    saveLanguage(value, localStorage)
    setPreferenceError(false)
    const owner = account.current?.id
    if (owner) {
      // Serialize explicit choices so a slow older save cannot overwrite a newer one.
      saves.current = saves.current.catch(() => {}).then(async () => {
        if (account.current?.id !== owner) return
        try { await profileService.setPreferredLanguage(value) }
        catch { if (account.current?.id === owner) setPreferenceError(true) }
      })
    }
  }, [])
  useEffect(() => {
    if (!user) return
    if (choice.current > 0) { setLanguage(readLanguage(localStorage)); return }
    const revision = choice.current
    const owner = user.id
    let cancelled = false
    const apply = (value: unknown) => {
      if (canApplySavedLanguage(cancelled, revision, choice.current, owner, account.current?.id) && isLanguage(value)) {
        setLanguageState(value); saveLanguage(value, localStorage)
      }
    }
    apply(user.preferredLanguage)
    void profileService.get().then(profile => apply(profile?.preferredLanguage)).catch(() => {})
    return () => { cancelled = true }
  }, [user, setLanguage]) // Preference changes never refetch business or analysis data.
  const setFontScale = useCallback((value: FontScale) => {
    setFontScaleState(value)
    try { localStorage.setItem('udyammitra-font-scale', value) } catch { /* Optional storage. */ }
  }, [])
  useEffect(() => { document.documentElement.lang = language; document.documentElement.dataset.fontScale = fontScale }, [fontScale, language])
  const value = useMemo(() => ({ language, setLanguage, fontScale, setFontScale, preferenceError,
    t: translations[language], text: (input: string | null | undefined) => localizeText(input, language),
    date: (input: string | number | Date) => formatDate(input, language) }), [fontScale, language, preferenceError, setFontScale, setLanguage])
  return <UiContext.Provider value={value}>{children}</UiContext.Provider>
}
