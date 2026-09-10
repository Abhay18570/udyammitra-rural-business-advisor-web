import { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { Brand } from '../components/common/Brand'
import { LanguageSelector } from '../components/layout/LanguageSelector'
import { useAuth } from '../context/authContextValue'
import { useUi } from '../i18n/uiContextValue'
import '../features/admin/admin.css'

export function AdminDashboardLayout() {
  const [open, setOpen] = useState(false)
  const { user, logout } = useAuth()
  const { text } = useUi()
  const navigate = useNavigate()
  return <div className="officer-layout">
    <a className="officer-skip" href="#officer-content">{text('Skip to main content')}</a>
    <aside className="officer-sidebar">
      <Brand inverse /><p>{text('Government Officer Portal')}</p>
      <button className="officer-menu" aria-expanded={open} aria-controls="officer-navigation" onClick={() => setOpen(value => !value)}>{text(open ? 'Close menu' : 'Open menu')}</button>
      <nav id="officer-navigation" className={open ? 'is-open' : ''} aria-label={text('Administration')} onKeyDown={event => { if (event.key === 'Escape') setOpen(false) }}>
        <NavLink to="/admin/dashboard" onClick={() => setOpen(false)}>{text('Dashboard')}</NavLink>
        <NavLink to="/admin/entrepreneurs" onClick={() => setOpen(false)}>{text('Entrepreneurs')}</NavLink>
        <NavLink to="/admin/analytics/geography" onClick={() => setOpen(false)}>{text('Geographic Analytics')}</NavLink>
        <p className="officer-future">{text('More administration tools are coming soon.')}</p>
        <button onClick={() => { logout(); navigate('/login', { replace: true }) }}>{text('Logout')}</button>
      </nav>
    </aside>
    <div className="officer-workspace"><header className="officer-header"><div><strong>{text('UdyamMitra Administration')}</strong><p>{user?.email}</p><span className="officer-badge">{text(user?.role === 'SUPER_ADMIN' ? 'Super Administrator' : 'Administrator')}</span></div><LanguageSelector /></header>
      <main id="officer-content" tabIndex={-1}><Outlet /></main>
    </div>
  </div>
}
