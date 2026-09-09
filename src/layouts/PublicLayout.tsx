import { Outlet, useLocation } from 'react-router-dom'
import { Footer } from '../components/layout/Footer'
import { PublicHeader } from '../components/layout/PublicHeader'
import { LandingFooter } from '../components/landing/LandingFooter'
import '../components/landing/landing.css'

export function PublicLayout() { const landing = useLocation().pathname === '/'; return <div className={landing ? "app-shell landing-shell" : "app-shell"}><PublicHeader landing={landing} /><main id="main-content" tabIndex={-1}><Outlet /></main>{landing ? <LandingFooter /> : <Footer />}</div> }
