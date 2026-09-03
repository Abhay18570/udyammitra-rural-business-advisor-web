import { Languages } from 'lucide-react'
import { useUi } from '../../i18n/uiContextValue'
import type { Language } from '../../i18n/translations'

export function LanguageSelector({ compact = false }: { compact?: boolean }) { const { language, setLanguage, t } = useUi(); return <label className="language-selector"><Languages aria-hidden="true" /><span className={compact ? 'sr-only' : ''}>{t.language}</span><select aria-label={t.language} value={language} onChange={event => setLanguage(event.target.value as Language)}><option value="en">English</option><option value="hi">हिन्दी</option><option value="mr">मराठी</option></select></label> }
