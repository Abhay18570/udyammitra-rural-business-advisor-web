import { useUi as useTextUi } from '../../i18n/uiContextValue'
import { LocalizedText } from '../../i18n/LocalizedText'
import { Languages } from 'lucide-react'
import { useUi } from '../../i18n/uiContextValue'
import type { Language } from '../../i18n/translations'

export function LanguageSelector({ compact = false }: { compact?: boolean }) {
  const { text: textUi } = useTextUi()
 const { language, setLanguage, t, preferenceError } = useUi(); return <label className="language-selector"><Languages aria-hidden="true" /><span className={compact ? 'sr-only' : ''}>{t.language}</span><select aria-label={textUi(t.language)} value={language} onChange={event => setLanguage(event.target.value as Language)}><option value="en"><LocalizedText value={"English"} /></option><option value="hi">हिन्दी</option><option value="mr">मराठी</option></select>{preferenceError && <span role="status"><LocalizedText value="Language saved on this device. Account preference could not be saved; try selecting the language again." /></span>}</label> }
