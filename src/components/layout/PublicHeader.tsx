import { Menu, X } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { NavLink } from 'react-router-dom'
import { useUi } from '../../i18n/uiContextValue'
import { Brand } from '../common/Brand'
import { ButtonLink } from '../ui/Button'
import { LanguageSelector } from './LanguageSelector'

const navTargets = ['/', '/how-it-works', '/opportunities', '/market-analysis', '/schemes', '/about']

export function PublicHeader() {
  const [open, setOpen] = useState(false)
  const { fontScale, setFontScale, t } = useUi()
  const menuButton = useRef<HTMLButtonElement>(null)
  useEffect(() => { if (!open) return; const closeOnEscape = (event: KeyboardEvent) => { if (event.key === 'Escape') { setOpen(false); menuButton.current?.focus() } }; document.addEventListener('keydown', closeOnEscape); return () => document.removeEventListener('keydown', closeOnEscape) }, [open])
  return <>
    <a className="skip-link" href="#main-content">{t.skip}</a>
    <div className="utility-bar"><div className="container"><div className="india-identity"><i aria-hidden="true"><b /><b /><b /></i><strong>{t.india}</strong><span>{t.prototype}</span></div><div className="utility-actions"><a href="#main-content">{t.skip}</a><div className="font-controls" aria-label="Text size"><button className={fontScale === 'small' ? 'active' : ''} onClick={() => setFontScale('small')} aria-label="Decrease text size">A-</button><button className={fontScale === 'normal' ? 'active' : ''} onClick={() => setFontScale('normal')} aria-label="Normal text size">A</button><button className={fontScale === 'large' ? 'active' : ''} onClick={() => setFontScale('large')} aria-label="Increase text size">A+</button></div><LanguageSelector /></div></div></div>
    <header className="site-header"><div className="container header-row"><Brand /><button ref={menuButton} className="menu-button" onClick={() => setOpen(!open)} aria-expanded={open} aria-controls="public-navigation" aria-label={`${open ? 'Close' : 'Open'} navigation`}>{open ? <X /> : <Menu />}</button><nav id="public-navigation" className={open ? 'nav nav--open' : 'nav'} aria-label="Main navigation">{t.nav.map((label, index) => <NavLink key={navTargets[index]} to={navTargets[index]} onClick={() => setOpen(false)}>{label}</NavLink>)}<NavLink to="/login" onClick={() => setOpen(false)}>{t.login}</NavLink><ButtonLink to="/register" className="public-register-link" onClick={() => setOpen(false)}>{t.getStarted}</ButtonLink></nav></div></header>
    {open && <button className="public-nav-backdrop" type="button" onClick={() => setOpen(false)} aria-label="Close navigation" />}
  </>
}
