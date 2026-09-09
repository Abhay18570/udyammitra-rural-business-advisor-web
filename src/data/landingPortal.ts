import { BriefcaseBusiness, Calculator, ChartNoAxesCombined, Landmark, MapPin, MessageSquareText } from 'lucide-react'
import { landingMessages as m } from '../i18n/landingMessages'

export const carouselSlides = [
  { id: 'discovery', image: 'rural-entrepreneur-woman.webp', alt: m.altWoman.en, eyebrow: m.discovery.en, title: m.discoveryTitle.en, description: m.discoveryText.en, action: m.opportunitiesCta.en, to: '/opportunities' },
  { id: 'market', image: 'rural-kirana-owner.webp', alt: m.altKirana.en, eyebrow: m.market.en, title: m.marketTitle.en, description: m.marketText.en, action: m.marketCta.en, to: '/market-analysis' },
  { id: 'finance', image: 'rural-tailoring-business.webp', alt: m.altTailor.en, eyebrow: m.finance.en, title: m.financeTitle.en, description: m.financeText.en, action: m.financeCta.en, to: '/financial-plan' },
  { id: 'scheme', image: 'rural-dairy-entrepreneur.webp', alt: m.altDairy.en, eyebrow: m.scheme.en, title: m.schemeTitle.en, description: m.schemeText.en, action: m.schemeCta.en, to: '/schemes' },
  { id: 'advisor', image: 'rural-agri-equipment.webp', alt: m.altAgri.en, eyebrow: m.advisor.en, title: m.advisorTitle.en, description: m.advisorText.en, action: m.soon.en, to: '/advisor', comingSoon: true },
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
