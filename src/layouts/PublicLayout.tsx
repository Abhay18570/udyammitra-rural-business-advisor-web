import { Outlet } from 'react-router-dom'
import { Footer } from '../components/layout/Footer'
import { PublicHeader } from '../components/layout/PublicHeader'
export function PublicLayout() { return <div className="app-shell"><PublicHeader /><main id="main-content"><Outlet /></main><Footer /></div> }
