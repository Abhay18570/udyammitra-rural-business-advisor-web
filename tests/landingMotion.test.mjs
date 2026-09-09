import './tsxLoader.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { readFileSync } from 'node:fs'
const { observeReveals } = await import('../src/components/landing/useRevealOnScroll.ts')
const { HomePage } = await import('../src/pages/public/HomePage.tsx')
const { HeroSlide } = await import('../src/components/landing/HeroCarousel.tsx')
const { UiContext } = await import('../src/i18n/uiContextValue.ts')
const { translations } = await import('../src/i18n/translations.ts')
const { localizeText } = await import('../src/i18n/localize.ts')
const { carouselSlides } = await import('../src/data/landingPortal.ts')
const { carouselReducer, canRotate } = await import('../src/components/landing/carouselState.ts')
const render = (element, language = 'en') => renderToStaticMarkup(
  React.createElement(UiContext.Provider, { value: { language, t: translations[language], text: value => localizeText(value, language) } },
    React.createElement(MemoryRouter, null, element)))

function observerFixture(count = 6) {
  let callback
  let options
  const watched = new Set()
  const unobserved = []
  let disconnected = false
  const targets = Array.from({ length: count }, () => {
    const classes = new Set()
    const properties = new Map()
    return { classes, properties,
      classList: { add: name => classes.add(name), remove: name => classes.delete(name) },
      style: { setProperty: (name, value) => properties.set(name, value), removeProperty: name => properties.delete(name) } }
  })
  const root = { querySelectorAll: () => targets }
  for (const target of targets) target.parentElement = root
  class Observer {
    constructor(fn, config) { callback = fn; options = config }
    observe(target) { watched.add(target) }
    unobserve(target) { watched.delete(target); unobserved.push(target) }
    disconnect() { disconnected = true; watched.clear() }
  }
  return { targets, root, Observer, watched, unobserved, emit: entries => callback(entries), get options() { return options }, get disconnected() { return disconnected } }
}

test('reveal observer animates once, staggers six steps, and cleans up on unmount', () => {
  const f = observerFixture()
  const cleanup = observeReveals(f.root, f.Observer, false)
  assert.equal(f.watched.size, 6)
  assert.equal(f.options.threshold, .08)
  for (let i = 0; i < 6; i++) assert.equal(f.targets[i].properties.get('--reveal-delay'), `${i * 60}ms`)
  const target = f.targets[0]
  f.emit([{ target, isIntersecting: false }])
  assert.equal(target.classes.size, 0)
  f.emit([{ target, isIntersecting: true }])
  assert.ok(target.classes.has('portal-revealed'))
  assert.equal(f.watched.has(target), false)
  f.emit([{ target, isIntersecting: false }, { target, isIntersecting: true }])
  assert.equal(f.unobserved.length, 1, 'scrolling a few pixels never replays the reveal')
  cleanup()
  assert.equal(f.disconnected, true)
  assert.equal(target.classes.size, 0)
  assert.equal(target.properties.size, 0)
})

test('missing IntersectionObserver and reduced motion require no hidden state or timers', () => {
  const f = observerFixture()
  observeReveals(f.root, undefined, false)()
  observeReveals(f.root, f.Observer, true)()
  assert.equal(f.watched.size, 0)
  for (const target of f.targets) {
    assert.equal(target.classes.size, 0)
    assert.equal(target.properties.size, 0)
  }
  const html = render(React.createElement(HomePage))
  assert.ok(html.includes('Find the Right Business for Your Local Market'))
  assert.ok(html.includes('Before You Invest'))
  assert.match(html, /data-reveal="fade-up" class="portal-service"/)
  assert.doesNotMatch(html, /portal-revealed|data-reveal[^>]*hidden|animation-delay|aria-busy/)
  assert.match(html, /Loading photograph/)
  assert.match(html, /href="\/market-analysis"/)
})

for (const language of ['en', 'hi', 'mr']) test(`all five slides immediately render translated highlight, support and CTAs in ${language}`, () => {
  let state = { index: 0, revision: 0 }
  for (let i = 0; i < 5; i++) {
    const slide = carouselSlides[state.index]
    const html = render(React.createElement(HeroSlide, { slide, active: true, first: i === 0, loadImage: true, imageState: 'error', onImageState() {} }), language)
    for (const key of ['eyebrow', 'title', 'highlight', 'description', 'support', 'action', 'secondaryAction']) {
      const value = localizeText(slide[key], language)
      assert.ok(html.includes(value), `${slide.id}.${key}`)
      if (language !== 'en' && key !== 'highlight') assert.notEqual(value, slide[key], `${slide.id}.${key} translation`)
    }
    assert.match(html, /portal-art/)
    assert.doesNotMatch(html, /class="portal-photo/)
    assert.ok(html.includes(`href="${slide.to}"`))
    const preserved = { ...state }
    render(React.createElement(HeroSlide, { slide, active: true, first: i === 0, loadImage: false, imageState: 'error', onImageState() {} }), 'mr')
    assert.deepEqual(state, preserved)
    state = carouselReducer(state, { type: 'next' }, 5)
  }
  assert.equal(state.index, 0)
  state = carouselReducer(state, { type: 'previous' }, 5)
  assert.equal(state.index, 4)
  assert.equal(carouselSlides[state.index].to, '/register')
  assert.equal(canRotate(true, false, false, false, false), false)
})

test('motion CSS preserves content without animations and avoids horizontal reveal transforms', () => {
  const css = readFileSync(new URL('../src/components/landing/landing.css', import.meta.url), 'utf8')
  assert.match(css, /prefers-reduced-motion: no-preference/)
  assert.match(css, /prefers-reduced-motion: reduce/)
  assert.match(css, /\[data-reveal\] \{ opacity: 1; transform: none;/)
  assert.doesNotMatch(css, /\[data-reveal\][^{]*\{[^}]*(visibility:\s*hidden|display:\s*none)/)
  assert.match(css, /:focus-within[^}]*animation: none/s)
  assert.match(css, /@keyframes portal-fade-up[^}]*translateY\(12px\)/)
  assert.match(css, /overflow-wrap: anywhere/)
  const hook = readFileSync(new URL('../src/components/landing/useRevealOnScroll.ts', import.meta.url), 'utf8')
  assert.doesNotMatch(hook, /setTimeout|setInterval/)
})
