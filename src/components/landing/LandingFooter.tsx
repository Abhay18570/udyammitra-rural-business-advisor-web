import { UdyamMitraLogo } from '../common/UdyamMitraLogo'
import { Link } from 'react-router-dom'
import { useUi } from '../../i18n/uiContextValue'
import { landingMessages as m } from '../../i18n/landingMessages'

const groups = [
  { title: 'Platform', links: [['About', '/#about-udyammitra'], [m.how.en, '/#how-it-works'], ['Market Analysis', '/market-analysis'], ['Business Opportunities', '/opportunities']] },
  { title: m.financialGuidance.en, links: [['Financial Plan', '/financial-plan'], ['Government Schemes', '/schemes']] },
  { title: 'Support', links: [['AI Advisor', '/advisor'], ['Documents', '/documents'], [m.accessibility.en, '/#landing-accessibility']] },
]
export function LandingFooter() {
  const { text, language, setLanguage } = useUi()
  return <footer data-reveal="fade-in" className="portal-footer"><div className="portal-container portal-footer__grid"><div><Link className="portal-footer-brand" to="/"><UdyamMitraLogo variant="transparent" size="small" decorative />UdyamMitra</Link><p>{text('Rural Business Advisory Platform')}</p><p>{text(m.independent.en)}</p></div>
    {groups.map(group => <div key={group.title}><h3>{text(group.title)}</h3>{group.links.map(([label, to]) => <Link key={to} to={to} reloadDocument={to.startsWith('/#')}>{text(label)}{(to === '/advisor' || to === '/documents') && <small> — {text(m.soon.en)}</small>}</Link>)}</div>)}
    <div><h3>{text('Languages')}</h3>{([['en', 'English'], ['hi', 'हिंदी'], ['mr', 'मराठी']] as const).map(([code, label]) => <button key={code} lang={code} aria-pressed={language === code} onClick={() => setLanguage(code)}>{label}</button>)}</div>
  </div><div id="landing-accessibility" className="portal-container portal-footer__access" tabIndex={-1}><strong>{text(m.accessibility.en)}</strong><p>{text(m.accessHelp.en)}</p></div><div className="portal-container portal-footer__bottom"><span>UdyamMitra · {text(m.prototype.en)}</span><div><Link to="/privacy">{text('Privacy')}</Link><Link to="/terms">{text('Terms')}</Link><Link to="/disclaimer">{text('Disclaimer')}</Link></div></div></footer>
}
