import { useAuth } from '../../context/authContextValue'
import { landingMessages as m } from '../../i18n/landingMessages'
import { useUi as useTextUi } from '../../i18n/uiContextValue'
import { LocalizedText } from '../../i18n/LocalizedText'
import { Menu, X } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { NavLink } from 'react-router-dom'
import { useUi } from '../../i18n/uiContextValue'
import { Brand } from '../common/Brand'
import { ButtonLink } from '../ui/Button'
import { LanguageSelector } from './LanguageSelector'

const navTargets = ['/', '/how-it-works', '/opportunities', '/market-analysis', '/government-schemes', '/about']

export function PublicHeader({ landing = false }: { landing?: boolean }) {
  const { isAuthenticated } = useAuth()
  const { text: textUi } = useTextUi()

  const [open, setOpen] = useState(false)
  const { fontScale, setFontScale, t } = useUi()
  const menuButton = useRef<HTMLButtonElement>(null)
  useEffect(() => { if (!open) return; const closeOnEscape = (event: KeyboardEvent) => { if (event.key === 'Escape') { setOpen(false); menuButton.current?.focus() } }; document.addEventListener('keydown', closeOnEscape); return () => document.removeEventListener('keydown', closeOnEscape) }, [open])
  return <>
    <a className="skip-link" href="#main-content">{t.skip}</a>
    <div className="utility-bar"><div className="container"><div className="india-identity"><i aria-hidden="true"><b /><b /><b /></i><strong>{t.india}</strong><span>{landing ? textUi(m.prototype.en) : t.prototype}</span></div><div className="utility-actions"><a href="#main-content">{t.skip}</a>{landing && <a href="#landing-accessibility">{textUi(m.accessibility.en)}</a>}<div className="font-controls" aria-label={textUi("Text size")}><button className={fontScale === 'small' ? 'active' : ''} onClick={() => setFontScale('small')} aria-label={textUi("Decrease text size")}><LocalizedText value={"A-"} /></button><button className={fontScale === 'normal' ? 'active' : ''} onClick={() => setFontScale('normal')} aria-label={textUi("Normal text size")}><LocalizedText value={"A"} /></button><button className={fontScale === 'large' ? 'active' : ''} onClick={() => setFontScale('large')} aria-label={textUi("Increase text size")}><LocalizedText value={"A+"} /></button></div><LanguageSelector /></div></div></div>
    <header className="site-header"><div className="container header-row"><Brand preserveName={landing} /><button ref={menuButton} className="menu-button" onClick={() => setOpen(!open)} aria-expanded={open} aria-controls="public-navigation" aria-label={textUi(`${open ? 'Close' : 'Open'} navigation`)}>{open ? <X /> : <Menu />}</button><nav id="public-navigation" className={open ? 'nav nav--open' : 'nav'} aria-label={textUi("Main navigation")}>{(landing ? [t.nav[0], textUi(m.how.en), t.nav[2], t.nav[3], t.nav[4], textUi('AI Advisor')] : t.nav).map((label, index) => landing && index === 1 ? <a key="how" href="#how-it-works" onClick={() => setOpen(false)}>{label}</a> : <NavLink end={index === 0} key={navTargets[index]} to={landing && index === 1 ? '/#how-it-works' : landing && index === 5 ? '/advisor' : navTargets[index]} onClick={() => setOpen(false)}><LocalizedText value={label} /></NavLink>)}<NavLink to="/login" onClick={() => setOpen(false)}>{t.login}</NavLink><ButtonLink to={landing && isAuthenticated ? "/dashboard" : "/register"} className="public-register-link" onClick={() => setOpen(false)}>{landing && isAuthenticated ? textUi("Dashboard") : t.getStarted}</ButtonLink></nav></div></header>
    {open && <button className="public-nav-backdrop" type="button" onClick={() => setOpen(false)} aria-label={textUi("Close navigation")} />}
  </>
}
