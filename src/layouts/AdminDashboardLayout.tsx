import { useEffect, useRef, useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { LayoutDashboard, LogOut, MapPinned, Menu, PanelLeftClose, PanelLeftOpen, Users, X } from 'lucide-react'
import { Brand } from '../components/common/Brand'
import { LanguageSelector } from '../components/layout/LanguageSelector'
import { useAuth } from '../context/authContextValue'
import { useUi } from '../i18n/uiContextValue'
import '../features/admin/admin.css'

const ADMIN_COLLAPSED_KEY = 'udyammitra.admin.sidebar.collapsed'

export function AdminDashboardLayout() {
  const [open, setOpen] = useState(false)
  const [collapsed, setCollapsed] = useState(() => {
    try {
      return localStorage.getItem(ADMIN_COLLAPSED_KEY) === 'true'
    } catch {
      return false
    }
  })
  const { user, logout } = useAuth()
  const { text } = useUi()
  const navigate = useNavigate()
  const menuButton = useRef<HTMLButtonElement>(null)
  const closeButton = useRef<HTMLButtonElement>(null)

  const closeSidebar = () => setOpen(false)
  const handleLogout = () => { logout(); navigate('/login', { replace: true }) }

  useEffect(() => {
    try {
      localStorage.setItem(ADMIN_COLLAPSED_KEY, String(collapsed))
    } catch {
      /* Storage is optional. */
    }
  }, [collapsed])

  useEffect(() => {
    const desktop = window.matchMedia('(min-width: 1024px)')
    const closeMobileDrawer = () => {
      if (desktop.matches) setOpen(false)
    }
    desktop.addEventListener('change', closeMobileDrawer)
    return () => desktop.removeEventListener('change', closeMobileDrawer)
  }, [])

  useEffect(() => {
    if (!open) return
    closeButton.current?.focus()
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setOpen(false)
        menuButton.current?.focus()
      }
    }
    document.addEventListener('keydown', closeOnEscape)
    return () => {
      document.body.style.overflow = previousOverflow
      document.removeEventListener('keydown', closeOnEscape)
    }
  }, [open])

  return (
    <div className={`officer-layout${collapsed ? ' officer-layout--collapsed' : ''}`}>
      <a className="officer-skip" href="#officer-content">{text('Skip to main content')}</a>
      <aside
        id="officer-sidebar"
        className={`officer-sidebar${open ? ' officer-sidebar--open' : ''}`}
        aria-label={text('Government Officer Portal')}
      >
        <div className="officer-sidebar__top">
          <Brand inverse />
          <button
            className="officer-sidebar__toggle"
            type="button"
            onClick={() => setCollapsed(value => !value)}
            aria-label={text(collapsed ? 'Expand sidebar' : 'Collapse sidebar')}
            title={text(collapsed ? 'Expand sidebar' : 'Collapse sidebar')}
            aria-expanded={!collapsed}
            aria-controls="officer-sidebar"
          >
            {collapsed ? <PanelLeftOpen size={20} aria-hidden="true" /> : <PanelLeftClose size={20} aria-hidden="true" />}
          </button>
          <button
            className="officer-sidebar__close"
            type="button"
            ref={closeButton}
            onClick={closeSidebar}
            aria-label={text('Close sidebar')}
          >
            <X size={20} aria-hidden="true" />
          </button>
        </div>
        <p className="officer-portal-title">{text('Government Officer Portal')}</p>
        <nav
          id="officer-navigation"
          aria-label={text('Administration')}
        >
          <NavLink
            to="/admin/dashboard"
            onClick={closeSidebar}
            aria-label={text('Dashboard')}
            title={text('Dashboard')}
          >
            <LayoutDashboard size={20} aria-hidden="true" />
            <span className="officer-nav__label">{text('Dashboard')}</span>
          </NavLink>
          <NavLink
            to="/admin/entrepreneurs"
            onClick={closeSidebar}
            aria-label={text('Entrepreneurs')}
            title={text('Entrepreneurs')}
          >
            <Users size={20} aria-hidden="true" />
            <span className="officer-nav__label">{text('Entrepreneurs')}</span>
          </NavLink>
          <NavLink
            to="/admin/analytics/geography"
            onClick={closeSidebar}
            aria-label={text('Geographic Analytics')}
            title={text('Geographic Analytics')}
          >
            <MapPinned size={20} aria-hidden="true" />
            <span className="officer-nav__label">{text('Geographic Analytics')}</span>
          </NavLink>
          <p className="officer-future">{text('More administration tools are coming soon.')}</p>
          <button
            type="button"
            className="officer-logout-btn"
            onClick={handleLogout}
            aria-label={text('Logout')}
            title={text('Logout')}
          >
            <LogOut size={20} aria-hidden="true" />
            <span className="officer-nav__label">{text('Logout')}</span>
          </button>
        </nav>
      </aside>
      {open && (
        <button
          className="officer-backdrop"
          type="button"
          onClick={closeSidebar}
          aria-label={text('Close sidebar')}
        />
      )}
      <div className="officer-workspace">
        <header className="officer-header">
          <button
            ref={menuButton}
            type="button"
            className="officer-menu"
            onClick={() => setOpen(true)}
            aria-label={text('Open sidebar')}
            aria-expanded={open}
            aria-controls="officer-sidebar"
          >
            <Menu size={22} aria-hidden="true" />
          </button>
          <div className="officer-header__meta">
            <strong>{text('UdyamMitra Administration')}</strong>
            <p>{user?.email}</p>
            <span className="officer-badge">{text(user?.role === 'SUPER_ADMIN' ? 'Super Administrator' : 'Administrator')}</span>
          </div>
          <LanguageSelector />
        </header>
        <main id="officer-content" tabIndex={-1}>
          <Outlet />
        </main>
      </div>
    </div>
  )
}
