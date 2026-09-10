import './tsxLoader.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'

const { UiContext } = await import('../src/i18n/uiContextValue.ts')
const { AuthContext } = await import('../src/context/authContextValue.ts')
const { translations } = await import('../src/i18n/translations.ts')
const { localizeText } = await import('../src/i18n/localize.ts')
const { landingMessages: m } = await import('../src/i18n/landingMessages.ts')
const { HomePage } = await import('../src/pages/public/HomePage.tsx')
const { LatestUpdatesBar } = await import('../src/components/landing/LatestUpdatesBar.tsx')
const { defaultHomeAlerts } = await import('../src/data/homeAlerts.ts')

const render = (element, language = 'en', authenticated = false) =>
  renderToStaticMarkup(
    React.createElement(
      AuthContext.Provider,
      { value: { isAuthenticated: authenticated } },
      React.createElement(
        UiContext.Provider,
        {
          value: {
            language,
            t: translations[language],
            text: v => localizeText(v, language),
            fontScale: 'normal',
            setFontScale() {},
            setLanguage() {},
          },
        },
        React.createElement(MemoryRouter, null, element)
      )
    )
  )

test('1. Latest Updates bar renders below navigation and above hero carousel on HomePage', () => {
  const html = render(React.createElement(HomePage), 'en')
  const tickerIndex = html.indexOf('class="latest-updates-bar"')
  const heroIndex = html.indexOf('class="portal-carousel"')
  assert.ok(tickerIndex !== -1, 'LatestUpdatesBar must be present')
  assert.ok(heroIndex !== -1, 'HeroCarousel must be present')
  assert.ok(tickerIndex < heroIndex, 'LatestUpdatesBar must render before HeroCarousel')
})

test('2. English label renders and all 6 alerts are present in primary and duplicated groups', () => {
  const html = render(React.createElement(LatestUpdatesBar), 'en')
  assert.ok(html.includes(m.latestUpdatesLabel.en), 'English label LATEST UPDATES renders')
  assert.equal(defaultHomeAlerts.length, 6, 'Must have exactly 6 prototype alerts')

  // Check all 6 English texts exist in data catalog
  const expectedAlertsEn = [
    'Explore government-supported financing options for eligible micro and small enterprises.',
    'Complete your entrepreneur profile to receive more relevant business and scheme guidance.',
    'Use Market Analysis to understand nearby competition and opportunities before investing.',
    'Prepare your Financial Plan to estimate project cost, own contribution and financing requirement.',
    'Review Government Schemes and verify eligibility from the linked official source before applying.',
    'Business Analysis combines profile, financial and market evidence to support better decisions.',
  ]

  expectedAlertsEn.forEach(alertText => {
    assert.ok(html.includes(alertText), `Alert must be present in HTML: ${alertText}`)
  })

  // Verify bullet separators are present
  assert.ok(html.includes('class="latest-updates-bar__bullet" aria-hidden="true">•</span>'))
})

test('3. Duplicated track group is present and marked aria-hidden for seamless loop', () => {
  const html = render(React.createElement(LatestUpdatesBar), 'en')
  assert.ok(
    html.includes('class="latest-updates-bar__group" aria-hidden="true"'),
    'Duplicated group must be aria-hidden for screen reader accessibility'
  )
  const totalGroups = html.match(/class="latest-updates-bar__group/g) || []
  assert.equal(totalGroups.length, 2, 'Exactly two groups in total (primary + clone)')
  const hiddenGroups = html.match(/class="latest-updates-bar__group"[^>]*aria-hidden="true"/g) || []
  assert.equal(hiddenGroups.length, 1, 'Exactly one duplicated group with aria-hidden="true"')
})


test('4. Old carousel elements (2/6 counter, previous/next arrows) are removed', () => {
  const html = render(React.createElement(LatestUpdatesBar), 'en')
  assert.equal(html.includes('1 / 6'), false, 'Index counter must be removed')
  assert.equal(html.includes('2 / 6'), false, 'Index counter must be removed')
  assert.equal(html.includes(m.previousUpdate.en), false, 'Previous button must be removed')
  assert.equal(html.includes(m.nextUpdate.en), false, 'Next button must be removed')
})

test('5. Hindi language switches label and all 6 alerts in scrolling track', () => {
  const html = render(React.createElement(LatestUpdatesBar), 'hi')
  assert.ok(html.includes(m.latestUpdatesLabel.hi), 'Hindi label नवीनतम अपडेट renders')

  const expectedAlertsHi = [
    'पात्र सूक्ष्म और लघु उद्यमों के लिए सरकार समर्थित वित्तीय विकल्पों की जानकारी देखें।',
    'अधिक प्रासंगिक व्यवसाय और योजना मार्गदर्शन के लिए अपना उद्यमी प्रोफ़ाइल पूरा करें।',
    'निवेश से पहले आसपास की प्रतिस्पर्धा और अवसरों को समझने के लिए बाजार विश्लेषण का उपयोग करें।',
    'परियोजना लागत, स्वयं का योगदान और वित्तीय आवश्यकता का अनुमान लगाने के लिए अपनी वित्तीय योजना तैयार करें।',
    'सरकारी योजनाओं की समीक्षा करें और आवेदन से पहले आधिकारिक स्रोत से पात्रता सत्यापित करें।',
    'व्यवसाय विश्लेषण बेहतर निर्णयों के लिए प्रोफ़ाइल, वित्तीय और बाजार साक्ष्यों को एक साथ प्रस्तुत करता है।',
  ]

  expectedAlertsHi.forEach(alertText => {
    assert.ok(html.includes(alertText), `Hindi alert must be in HTML: ${alertText}`)
  })
})

test('6. Marathi language switches label and all 6 alerts in scrolling track', () => {
  const html = render(React.createElement(LatestUpdatesBar), 'mr')
  assert.ok(html.includes(m.latestUpdatesLabel.mr), 'Marathi label नवीन अपडेट्स renders')

  const expectedAlertsMr = [
    'पात्र सूक्ष्म आणि लघु उद्योगांसाठी शासन-समर्थित वित्तपुरवठा पर्यायांची माहिती पहा.',
    'अधिक संबंधित व्यवसाय आणि योजना मार्गदर्शनासाठी आपले उद्योजक प्रोफाइल पूर्ण करा.',
    'गुंतवणुकीपूर्वी जवळील स्पर्धा आणि संधी समजून घेण्यासाठी बाजार विश्लेषण वापरा.',
    'प्रकल्प खर्च, स्वतःचे योगदान आणि वित्तीय गरज यांचा अंदाज घेण्यासाठी आपली आर्थिक योजना तयार करा.',
    'शासकीय योजनांचा आढावा घ्या आणि अर्ज करण्यापूर्वी अधिकृत स्रोतावरून पात्रता पडताळा.',
    'व्यवसाय विश्लेषण चांगल्या निर्णयांसाठी प्रोफाइल, आर्थिक आणि बाजारातील पुरावे एकत्रित करते.',
  ]

  expectedAlertsMr.forEach(alertText => {
    assert.ok(html.includes(alertText), `Marathi alert must be in HTML: ${alertText}`)
  })
})

test('7. Accessibility attributes, pause/play toggle, and region labels render correctly', () => {
  for (const language of ['en', 'hi', 'mr']) {
    const html = render(React.createElement(LatestUpdatesBar), language)
    assert.ok(html.includes('role="region"'))
    assert.ok(html.includes(`aria-label="${localizeText(m.latestUpdatesRegion.en, language)}"`))
    assert.ok(html.includes(`aria-label="${localizeText(m.pauseUpdates.en, language)}"`))
    assert.ok(html.includes('aria-pressed="false"'))
  }
})

test('8. CSS includes continuous right-to-left marquee animation and reduced motion rules', () => {
  const css = readFileSync('src/components/landing/landing.css', 'utf8')
  assert.ok(css.includes('.latest-updates-bar'))
  assert.ok(css.includes('.latest-updates-bar__viewport'))
  assert.ok(css.includes('.latest-updates-bar__track'))
  assert.ok(css.includes('animation: newsTickerScroll'))
  assert.ok(css.includes('@keyframes newsTickerScroll'))
  assert.ok(css.includes('transform: translateX(-50%)'))
  assert.ok(css.includes('animation-play-state: paused'))
  assert.ok(css.includes('@media (prefers-reduced-motion: reduce)'))
})
