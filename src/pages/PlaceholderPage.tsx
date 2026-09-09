import { LanguageSelector } from '../components/layout/LanguageSelector'
import { useUi as useTextUi } from '../i18n/uiContextValue'
import { LocalizedText } from '../i18n/LocalizedText'
import { Construction } from 'lucide-react'
import { useLocation } from 'react-router-dom'
import { Breadcrumbs, PageHeading } from '../components/ui/Navigation'
export function PlaceholderPage({ title, area = 'Module' }: { title?: string; area?: string }) {
  const { text: textUi } = useTextUi()
 const { pathname } = useLocation(); const derived = pathname.split('/').filter(Boolean).pop()?.replaceAll('-', ' ') ?? 'Page'; const name = title ?? derived.replace(/\b\w/g, c => c.toUpperCase()); return <section className="placeholder container"><Breadcrumbs items={[{ label: 'Home', to: '/' }, { label: name }]} /><PageHeading eyebrow={textUi(area)} title={textUi(name)} description={textUi("This module is under development and will be connected in a future implementation phase.")} />{pathname === '/settings' && <LanguageSelector />}<div className="under-development"><Construction /><h2><LocalizedText value={"Coming in the next phase"} /></h2><p><LocalizedText value={"The routing and layout foundation for this module is ready. No simulated data or functionality has been added."} /></p></div></section> }
