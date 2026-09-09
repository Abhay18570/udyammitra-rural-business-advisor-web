import { BriefcaseBusiness, Calculator, ChartNoAxesCombined, Landmark, MapPin, MessageSquareText } from 'lucide-react'
import { landingMessages as m } from '../i18n/landingMessages'

export const carouselSlides = [
  { id: 'discovery', image: 'Bhaji.jpg', objectPosition: '55% 40%', alt: m.altWoman.en, eyebrow: m.discovery.en, title: m.discoveryTitle.en, highlight: m.heroDiscoveryHighlight.en, description: m.heroDiscoveryDescription.en, support: m.heroDiscoverySupport.en, action: m.opportunitiesCta.en, to: '/opportunities', secondaryAction: m.how.en, secondaryTo: '#how-it-works' },
  { id: 'market', image: 'general.jpg', objectPosition: '45% 45%', alt: m.altKirana.en, eyebrow: m.heroMarketEyebrow.en, title: m.heroMarketTitle.en, highlight: m.heroMarketHighlight.en, description: m.heroMarketDescription.en, support: m.heroMarketSupport.en, action: m.marketCta.en, to: '/market-analysis', secondaryAction: m.how.en, secondaryTo: '#how-it-works' },
  { id: 'finance', image: 'kirana.jpeg', objectPosition: '32% 40%', alt: m.altTailor.en, eyebrow: m.heroFinanceEyebrow.en, title: m.heroFinanceTitle.en, highlight: m.heroFinanceHighlight.en, description: m.heroFinanceDescription.en, support: m.heroFinanceSupport.en, action: m.financeCta.en, to: '/financial-plan', secondaryAction: m.how.en, secondaryTo: '#how-it-works' },
  { id: 'scheme', image: 'masalas.jpg', objectPosition: '55% 50%', alt: m.altDairy.en, eyebrow: m.scheme.en, title: m.heroSchemeTitle.en, highlight: m.heroSchemeHighlight.en, description: m.heroSchemeDescription.en, support: m.heroSchemeSupport.en, action: m.schemeCta.en, to: '/schemes', secondaryAction: m.how.en, secondaryTo: '#how-it-works' },
  { id: 'advisor', image: 'tea.jpg', objectPosition: '50% 40%', alt: m.altAgri.en, eyebrow: m.heroLanguageEyebrow.en, title: m.heroLanguageTitle.en, highlight: m.heroLanguageHighlight.en, description: m.heroLanguageDescription.en, support: m.heroLanguageSupport.en, action: 'Get Started', to: '/register', secondaryAction: m.how.en, secondaryTo: '#how-it-works' },
]
export type CarouselSlide = typeof carouselSlides[number]
export const landingServices = [
  { id: 'market', icon: MapPin, title: 'Market Analysis', feature: m.evidence.en, description: m.marketShort.en, detail: m.marketText.en, to: '/market-analysis' },
  { id: 'opportunities', icon: BriefcaseBusiness, title: 'Business Opportunities', feature: m.opportunity.en, description: m.oppShort.en, detail: m.discoveryText.en, to: '/opportunities' },
  { id: 'finance', icon: Calculator, title: m.finance.en, feature: m.finance.en, description: m.financeShort.en, detail: m.financeText.en, to: '/financial-plan' },
  { id: 'schemes', icon: Landmark, title: 'Government Schemes', feature: m.scheme.en, description: m.schemeShort.en, detail: m.schemeText.en, to: '/schemes' },
]
export const exploreServices = [...landingServices,
  { id: 'analysis', icon: ChartNoAxesCombined, title: 'Business Analysis', description: m.analysisText.en, to: '/business-analysis' },
  { id: 'advisor', icon: MessageSquareText, title: 'AI Advisor', description: m.advisorText.en, to: '/advisor', comingSoon: true },
]
export const journeySteps = [m.step1.en, m.step2.en, m.step3.en, m.step4.en, m.step5.en, m.step6.en]
// Editorial summaries of scheme-v1 in backend/app/scheme_rules.py, not eligibility rules.
// The public page does not call the authenticated guidance endpoint or calculate eligibility.
export const schemeHighlights = [
  { id: 'micro', title: m.micro.en, range: m.microRange.en, details: [m.funding.en, m.microLoan.en, m.microRate.en, m.microTenure.en] },
  { id: 'term', title: m.term.en, range: m.termRange.en, details: [m.funding.en, m.termLoan.en, m.termRate.en, m.termTenure.en] },
]
export const landingImageFolder = '/assets/landing/carousel/'
