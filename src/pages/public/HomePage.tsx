import { LatestUpdatesBar } from '../../components/landing/LatestUpdatesBar'
import { HeroCarousel } from '../../components/landing/HeroCarousel'
import { EntrepreneurJourney, ExploreUdyamMitra, FeatureSection, QuickAccess, SchemeHighlight, TrustStrip } from '../../components/landing/PortalSections'

export function HomePage() {
  return (
    <div className="landing-portal">
      <LatestUpdatesBar />
      <HeroCarousel />
      <QuickAccess />
      <FeatureSection />
      <ExploreUdyamMitra />
      <EntrepreneurJourney />
      <SchemeHighlight />
      <TrustStrip />
    </div>
  )
}
