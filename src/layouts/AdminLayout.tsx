import { LanguageSelector } from '../components/layout/LanguageSelector'
import { LocalizedText } from '../i18n/LocalizedText'
import { NavLink, Outlet } from 'react-router-dom'
import { Brand } from '../components/common/Brand'
const adminLinks = ['dashboard', 'users', 'businesses', 'schemes', 'knowledge', 'map', 'reports', 'settings']
export function AdminLayout() { return <div className="admin-layout"><aside><Brand inverse /><strong><LocalizedText value={"Administration"} /></strong><nav>{adminLinks.map(link => <NavLink key={link} to={`/admin/${link}`}><LocalizedText value={link[0].toUpperCase() + link.slice(1)} /></NavLink>)}</nav></aside><main id="main-content"><LanguageSelector /><Outlet /></main></div> }
