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
const { landingMessages: messages } = await import('../src/i18n/landingMessages.ts')
const { HomePage } = await import('../src/pages/public/HomePage.tsx')
const { HeroSlide, CarouselControls } = await import('../src/components/landing/HeroCarousel.tsx')
const { PublicHeader } = await import('../src/components/layout/PublicHeader.tsx')
const { LandingFooter } = await import('../src/components/landing/LandingFooter.tsx')
const { carouselSlides, landingServices, schemeHighlights } = await import('../src/data/landingPortal.ts')
const { carouselReducer, canRotate, scheduleRotation, ROTATION_MS } = await import('../src/components/landing/carouselState.ts')
const render = (element, language = 'en', authenticated = false) => renderToStaticMarkup(
  React.createElement(AuthContext.Provider, { value: { isAuthenticated: authenticated } },
    React.createElement(UiContext.Provider, { value: { language, t: translations[language], text: v => localizeText(v, language), fontScale: 'normal', setFontScale() {}, setLanguage() {} } },
      React.createElement(MemoryRouter, null, element))))

for (const language of ['en', 'hi', 'mr']) test(`landing, carousel, first slide and footer render in ${language}`, () => {
  const html = render(React.createElement(HomePage), language)
  assert.ok(html.includes(messages.discoveryTitle[language]))
  assert.ok(html.includes(messages.quick[language]))
  assert.ok(html.includes(messages.journey[language]))
  assert.ok(html.includes(messages.disclaimer[language]))
  assert.equal((html.match(/class="portal-slide portal-slide--/g) || []).length, 5)
  assert.equal((html.match(/aria-hidden="true" inert=""/g) || []).length, 4)
  assert.ok(html.includes(`aria-label="${messages.next[language]}"`))
  assert.ok(html.includes('fetchPriority="high"'))
  assert.equal((html.match(/<img class="portal-photo /g) || []).length, 1, 'only first photograph requested on initial render')
  const footer = render(React.createElement(LandingFooter), language)
  assert.ok(footer.includes(messages.prototype[language]))
  assert.ok(footer.includes(messages.independent[language]))
  assert.ok(footer.includes('href="/financial-plan"'))
})

test('new message catalog is complete and uses runtime localization in every language', () => {
  for (const row of Object.values(messages)) for (const lang of ['en', 'hi', 'mr']) {
    assert.ok(row[lang].trim())
    assert.equal(localizeText(row.en, lang), row[lang], row.en)
  }
})

test('next, previous, indicators, wraparound and timer resets use the same reducer', () => {
  let state = { index: 0, revision: 0 }
  state = carouselReducer(state, { type: 'next' }, 5)
  assert.equal(state.index, 1)
  state = carouselReducer(state, { type: 'previous' }, 5)
  assert.equal(state.index, 0)
  state = carouselReducer(state, { type: 'previous' }, 5)
  assert.equal(state.index, 4)
  state = carouselReducer(state, { type: 'next' }, 5)
  assert.equal(state.index, 0)
  state = carouselReducer(state, { type: 'select', index: 3 }, 5)
  assert.equal(state.index, 3)
  const revision = state.revision
  state = carouselReducer(state, { type: 'select', index: 3 }, 5)
  assert.equal(state.revision, revision + 1, 'clicking current dot also resets timer')
  const preserved = { ...state }
  for (const language of ['en', 'hi', 'mr']) {
    const html = render(React.createElement(HeroSlide, { slide: carouselSlides[state.index], active: true, first: false, loadImage: false, imageState: 'error', onImageState() {} }), language)
    assert.ok(html.includes(messages.schemeTitle[language]))
    assert.deepEqual(state, preserved, 'locale is not carousel state')
  }
})

test('rotation schedules six seconds, advances, and cancels on cleanup/manual reset', () => {
  let state = { index: 0, revision: 0 }
  let callback
  const cancelled = []
  const cleanup = scheduleRotation(() => { state = carouselReducer(state, { type: 'tick' }, 5) }, true,
    (fn, delay) => { assert.equal(delay, 6000); callback = fn; return 42 }, id => cancelled.push(id))
  assert.equal(ROTATION_MS, 6000)
  callback()
  assert.equal(state.index, 1)
  cleanup()
  assert.deepEqual(cancelled, [42])
  scheduleRotation(() => assert.fail('should not rotate'), false, () => assert.fail('should not schedule'))()
})

test('reduced motion, hidden tab, hover, focus, and explicit pause all stop rotation', () => {
  assert.equal(canRotate(false, false, false, false, false), true)
  for (let i = 0; i < 5; i++) {
    const flags = Array(5).fill(false); flags[i] = true
    assert.equal(canRotate(...flags), false)
  }
})

test('image loading, loaded fade class, missing-image fallback and inactive focus isolation', () => {
  const props = { slide: carouselSlides[0], active: true, first: true, loadImage: true, onImageState() {} }
  const loading = render(React.createElement(HeroSlide, { ...props, imageState: 'loading' }))
  assert.match(loading, /role="status"/)
  assert.match(loading, /Loading photograph/)
  assert.doesNotMatch(loading, /portal-photo is-loaded/)
  const loaded = render(React.createElement(HeroSlide, { ...props, imageState: 'loaded' }))
  assert.match(loaded, /portal-photo is-loaded/)
  assert.doesNotMatch(loaded, /Loading photograph/)
  const missing = render(React.createElement(HeroSlide, { ...props, imageState: 'error' }))
  assert.doesNotMatch(missing, /<img class="portal-photo /)
  assert.match(missing, /portal-art/)
  assert.ok(missing.includes(messages.discoveryTitle.en))
  const inactive = render(React.createElement(HeroSlide, { ...props, active: false, imageState: 'error' }))
  assert.match(inactive, /aria-hidden="true" inert=""/)
})

test('accessible controls expose all five destinations and pause state', () => {
  const html = render(React.createElement(CarouselControls, { text: v => v, index: 2, paused: true, onPrevious() {}, onNext() {}, onSelect() {}, onPause() {} }))
  assert.match(html, /aria-label="Previous slide"/)
  assert.match(html, /aria-label="Next slide"/)
  assert.match(html, /aria-label="Play slideshow" aria-pressed="true"/)
  assert.equal((html.match(/aria-current="true"/g) || []).length, 1)
  for (let i = 1; i <= 5; i++) assert.ok(html.includes(`aria-label="Slide ${i}:`))
})

test('quick services, scheme CTA and auth-aware Get Started point to actual routes', () => {
  const html = render(React.createElement(HomePage))
  for (const service of landingServices) assert.ok(html.includes(`href="${service.to}"`))
  assert.match(html, /href="\/schemes"[^>]*>Check Scheme Guidance/)
  const loggedOut = render(React.createElement(PublicHeader, { landing: true }))
  assert.match(loggedOut, /href="\/register"/)
  assert.match(loggedOut, /href="#how-it-works"/)
  assert.match(loggedOut, /aria-controls="public-navigation"/)
  assert.match(loggedOut, /aria-current="page"[^>]*href="\/"/)
  assert.match(render(React.createElement(PublicHeader, { landing: true }), 'mr', true), /href="\/dashboard"/)
  const routes = readFileSync(new URL('../src/routes/AppRouter.tsx', import.meta.url), 'utf8')
  for (const path of ['dashboard', 'onboarding', 'profile', 'market-analysis', 'opportunities', 'financial-plan', 'business-analysis', 'schemes']) assert.ok(routes.includes(`path="${path}"`))
  assert.doesNotMatch(html, /financial-plan\/preview/)
  assert.match(html, /Coming Soon/)
})

test('scheme summaries match the canonical prototype metadata, with no landing calculations', () => {
  const rules = readFileSync(new URL('../backend/app/scheme_rules.py', import.meta.url), 'utf8')
  for (const amount of ['140000.00', '5000000.00', '125000.00', '4500000.00', '6.50', '8.00']) assert.ok(rules.includes(`"${amount}"`))
  assert.match(rules, /36, 3/); assert.match(rules, /84, 6/)
  assert.ok(schemeHighlights[0].details.includes('Maximum loan ₹1.25 lakh'))
  assert.ok(schemeHighlights[1].details.includes('Maximum loan ₹45 lakh'))
})

test('responsive CSS uses flexible grids, mobile menu, natural hero height and reduced motion', () => {
  const css = readFileSync(new URL('../src/components/landing/landing.css', import.meta.url), 'utf8')
  assert.match(css, /repeat\(4,minmax\(0,1fr\)\)/)
  assert.match(css, /@media\(max-width:479px\)/)
  assert.match(css, /@media\(max-width:1100px\)/)
  assert.match(css, /prefers-reduced-motion:reduce/)
  assert.match(css, /grid-area:1\/1/)
  assert.doesNotMatch(css, /\.portal-slide__body[^}]*[;{]\s*height:/)
})


test('actual control button handlers change selection and pause without losing selected language', () => {
  let state = { index: 0, revision: 0 }
  let paused = false
  let language = 'en'
  const dispatch = action => { state = carouselReducer(state, action, 5) }
  const controlTree = () => CarouselControls({ text: v => localizeText(v, language), index: state.index, paused,
    onPrevious: () => dispatch({ type: 'previous' }), onNext: () => dispatch({ type: 'next' }),
    onSelect: index => dispatch({ type: 'select', index }), onPause: () => { paused = !paused } })
  const buttons = tree => {
    const found = []
    function walk(node) {
      if (!node || typeof node !== 'object') return
      if (node.type === 'button') found.push(node)
      React.Children.forEach(node.props?.children, walk)
    }
    walk(tree)
    return found
  }
  buttons(controlTree())[6].props.onClick()
  assert.equal(state.index, 1)
  buttons(controlTree())[0].props.onClick()
  assert.equal(state.index, 0)
  buttons(controlTree())[4].props.onClick()
  assert.equal(state.index, 3)
  for (language of ['hi', 'mr']) {
    const selected = buttons(controlTree()).filter(button => button.props['aria-current'] === 'true')
    assert.equal(selected.length, 1)
    assert.ok(selected[0].props['aria-label'].includes(localizeText(carouselSlides[3].eyebrow, language)))
    assert.equal(state.index, 3)
  }
  buttons(controlTree())[7].props.onClick()
  assert.equal(paused, true)
  assert.equal(buttons(controlTree())[7].props['aria-label'], messages.play.mr)
})
