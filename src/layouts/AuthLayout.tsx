import { LocalizedText } from '../i18n/LocalizedText'
import { Outlet } from 'react-router-dom'
import { BarChart3, Calculator, Landmark, MapPinned } from 'lucide-react'
import { Brand } from '../components/common/Brand'
const capabilities = [{ icon: MapPinned, label: 'Local Market Analysis' }, { icon: BarChart3, label: 'Business Opportunity Guidance' }, { icon: Calculator, label: 'Financial Planning' }, { icon: Landmark, label: 'Scheme Assistance' }]
export function AuthLayout() { return <div className="auth-layout"><aside><Brand inverse /><div><span className="eyebrow"><LocalizedText value={"Build with confidence"} /></span><h1><LocalizedText value={"Better business decisions begin with better local information."} /></h1><p><LocalizedText value={"Practical decision support for aspiring and existing rural entrepreneurs."} /></p><div className="auth-capabilities">{capabilities.map(({ icon: Icon, label }) => <span key={label}><Icon aria-hidden="true" /><LocalizedText value={label} /></span>)}</div></div><small><LocalizedText value={"UdyamMitra · Educational prototype"} /></small></aside><main id="main-content"><Outlet /></main></div> }
