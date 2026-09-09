import { ArrowRight, Check, Languages, ShieldCheck } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useUi } from '../../i18n/uiContextValue'
import { landingMessages as m } from '../../i18n/landingMessages'
import { exploreServices, journeySteps, landingServices, schemeHighlights } from '../../data/landingPortal'

function Heading({ eyebrow, title, description }: { eyebrow?: string; title: string; description?: string }) {
  const { text } = useUi()
  return <div data-reveal="fade-up" className="portal-heading">{eyebrow && <span className="portal-kicker">{text(eyebrow)}</span>}<h2>{text(title)}</h2>{description && <p>{text(description)}</p>}</div>
}
export function QuickAccess() {
  const { text } = useUi()
  return <section className="portal-section portal-quick"><div className="portal-container"><Heading eyebrow={m.quick.en} title={m.services.en} />
    <div className="portal-grid portal-grid--four">{landingServices.map(({ id, icon: Icon, title, description, to }) => <Link data-reveal="fade-up" className="portal-service" key={id} to={to}><Icon aria-hidden="true" /><h3>{text(title)}</h3><p>{text(description)}</p><ArrowRight className="portal-service__arrow" aria-hidden="true" /></Link>)}</div>
  </div></section>
}
export function FeatureSection() {
  const { text } = useUi()
  return <section className="portal-section" id="about-udyammitra"><div className="portal-container"><Heading title={m.helps.en} description={m.helpsIntro.en} /><div className="portal-grid portal-grid--four">{landingServices.map(({ id, icon: Icon, feature, detail }) => <article data-reveal="fade-up" className="portal-feature" key={id}><span className="portal-icon"><Icon aria-hidden="true" /></span><h3>{text(feature)}</h3><p>{text(detail)}</p></article>)}</div></div></section>
}
export function ExploreUdyamMitra() {
  const { text, t } = useUi()
  return <section className="portal-section portal-section--tinted"><div className="portal-container"><Heading title={m.explore.en} description={m.exploreIntro.en} /><div className="portal-grid portal-grid--three">{exploreServices.map(service => <article data-reveal="fade-up" className="portal-explore" key={service.id}><service.icon aria-hidden="true" /><h3>{text(service.title)}</h3><p>{text(service.description)}</p>{'comingSoon' in service && service.comingSoon ? <span className="portal-status">{text(m.soon.en)}</span> : <Link to={service.to} aria-label={`${t.learn}: ${text(service.title)}`}>{t.learn}<ArrowRight aria-hidden="true" size={17} /></Link>}</article>)}</div></div></section>
}
export function EntrepreneurJourney() {
  const { text } = useUi()
  return <section className="portal-section" id="how-it-works"><div className="portal-container"><Heading eyebrow={m.how.en} title={m.journey.en} description={m.journeyIntro.en} /><ol className="portal-journey">{journeySteps.map((step, i) => <li data-reveal="fade-up" key={i}><span>{String(i + 1).padStart(2, '0')}</span><h3>{text(step)}</h3></li>)}</ol></div></section>
}
export function SchemeHighlight() {
  const { text } = useUi()
  return <section className="portal-section portal-schemes"><div className="portal-container"><Heading title={m.scheme.en} description={m.schemeIntro.en} /><div className="portal-grid portal-grid--two">{schemeHighlights.map(scheme => <article data-reveal="fade-up" className="portal-scheme" key={scheme.id}><span className="portal-kicker">{text(scheme.title)}</span><h3>{text(scheme.range)}</h3><ul>{scheme.details.map(detail => <li key={detail}><Check aria-hidden="true" size={18} />{text(detail)}</li>)}</ul></article>)}</div><Link className="portal-button" to="/schemes">{text(m.schemeCta.en)}<ArrowRight aria-hidden="true" size={18} /></Link></div></section>
}
export function TrustStrip() {
  const { text } = useUi()
  return <section className="portal-section portal-trust"><div className="portal-container"><Heading title={m.trust.en} /><div className="portal-grid portal-grid--four">{[m.trust1.en, m.trust2.en, m.trust3.en].map(item => <div data-reveal="fade-in" key={item}><ShieldCheck aria-hidden="true" /><span>{text(item)}</span></div>)}<div data-reveal="fade-in"><Languages aria-hidden="true" /><span>English · हिंदी · मराठी</span></div></div><p className="portal-disclaimer">{text(m.disclaimer.en)}</p></div></section>
}
