import { LanguageSelector } from '../components/layout/LanguageSelector'
import { useUi as useTextUi } from '../i18n/uiContextValue'
import { LocalizedText } from '../i18n/LocalizedText'
import { LogOut, Menu, PanelLeftClose, PanelLeftOpen, X } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { Brand } from '../components/common/Brand'
import { userNavigation, userUtilityNavigation } from '../config/navigation'
import { useAuth } from '../context/authContextValue'

const collapsedPreference = 'udyammitra-sidebar-collapsed'

export function UserDashboardLayout() {
  const { text: textUi } = useTextUi()

  const [open, setOpen] = useState(false)
  const [collapsed, setCollapsed] = useState(() => {
    try { return localStorage.getItem(collapsedPreference) === 'true' } catch { return false }
  })
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const menuButton = useRef<HTMLButtonElement>(null)
  const closeButton = useRef<HTMLButtonElement>(null)
  const initials = user?.fullName.split(' ').map(part => part[0]).slice(0, 2).join('').toUpperCase() ?? 'UM'
  const closeSidebar = () => setOpen(false)
  const handleLogout = () => { logout(); navigate('/login', { replace: true }) }

  useEffect(() => {
    try { localStorage.setItem(collapsedPreference, String(collapsed)) } catch { /* Storage is optional. */ }
  }, [collapsed])

  useEffect(() => {
    const desktop = window.matchMedia('(min-width: 1024px)')
    const closeMobileDrawer = () => { if (desktop.matches) setOpen(false) }
    desktop.addEventListener('change', closeMobileDrawer)
    return () => desktop.removeEventListener('change', closeMobileDrawer)
  }, [])

  useEffect(() => {
    if (!open) return
    closeButton.current?.focus()
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { setOpen(false); menuButton.current?.focus() }
    }
    document.addEventListener('keydown', closeOnEscape)
    return () => {
      document.body.style.overflow = previousOverflow
      document.removeEventListener('keydown', closeOnEscape)
    }
  }, [open])

  return (
    <div className={`dashboard-layout${collapsed ? ' dashboard-layout--collapsed' : ''}`}>
      <aside id="dashboard-sidebar" className={open ? 'sidebar sidebar--open' : 'sidebar'} aria-label={textUi("Entrepreneur workspace navigation")}>
        <div className="sidebar__top">
          <Brand inverse />
          <button className="sidebar__toggle" type="button" onClick={() => setCollapsed(value => !value)}
            aria-label={textUi(collapsed ? 'Expand sidebar' : 'Collapse sidebar')}
            title={textUi(collapsed ? 'Expand sidebar' : 'Collapse sidebar')}
            aria-expanded={!collapsed} aria-controls="dashboard-sidebar">
            {collapsed ? <PanelLeftOpen aria-hidden="true" /> : <PanelLeftClose aria-hidden="true" />}
          </button>
          <button className="sidebar__close" type="button" ref={closeButton} onClick={closeSidebar} aria-label={textUi("Close sidebar")}><X aria-hidden="true" /></button>
        </div>
        <nav aria-label={textUi("Dashboard navigation")}>
          {userNavigation.map(({ label, to, icon: Icon }) => (
            <NavLink key={to} to={to} onClick={closeSidebar} aria-label={textUi(label)} title={textUi(label)}>
              <Icon size={19} aria-hidden="true" /><span className="sidebar__label"><LocalizedText value={label} /></span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar__bottom">
          {userUtilityNavigation.map(({ label, to, icon: Icon }) => (
            <NavLink key={to} to={to} onClick={closeSidebar} aria-label={textUi(label)} title={textUi(label)}>
              <Icon size={19} aria-hidden="true" /><span className="sidebar__label"><LocalizedText value={label} /></span>
            </NavLink>
          ))}
          <button type="button" onClick={handleLogout} aria-label={textUi("Logout")} title={textUi("Logout")}><LogOut size={19} aria-hidden="true" /><span className="sidebar__label"><LocalizedText value={"Logout"} /></span></button>
        </div>
      </aside>
      {open && <button className="sidebar-backdrop" type="button" onClick={closeSidebar} aria-label={textUi("Close sidebar")} />}
      <div className="dashboard-main">
        <header>
          <button ref={menuButton} type="button" onClick={() => setOpen(true)} aria-label={textUi("Open sidebar")} aria-expanded={open} aria-controls="dashboard-sidebar"><Menu aria-hidden="true" /></button>
          <span className="workspace-title"><LocalizedText value={"UdyamMitra Workspace"} /></span>
          <LanguageSelector compact /><span className="avatar" title={user?.fullName}>{initials}</span>
        </header>
        <main id="main-content"><Outlet /></main>
      </div>
    </div>
  )
}
