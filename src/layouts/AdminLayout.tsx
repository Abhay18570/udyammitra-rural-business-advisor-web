import { NavLink, Outlet } from 'react-router-dom'
import { Brand } from '../components/common/Brand'
const adminLinks = ['dashboard', 'users', 'businesses', 'schemes', 'knowledge', 'map', 'reports', 'settings']
export function AdminLayout() { return <div className="admin-layout"><aside><Brand inverse /><strong>Administration</strong><nav>{adminLinks.map(link => <NavLink key={link} to={`/admin/${link}`}>{link[0].toUpperCase() + link.slice(1)}</NavLink>)}</nav></aside><main id="main-content"><Outlet /></main></div> }
