import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'

import './tsxLoader.mjs'
const { EvidenceMap } = await import('../src/features/marketAnalysis/MarketMap.tsx')
const { nearbyMapPoints } = await import('../src/features/marketAnalysis/evidenceMapModel.ts')
const props = { latitude: 19.2, longitude: 73.1, title: 'Evidence', centreName: 'Village', radiusMeters: 5000, points: [], textLabel: 'Business list' }
const { UiContext } = await import('../src/i18n/uiContextValue.ts')
const { translations } = await import('../src/i18n/translations.ts')
const { localizeText, formatDate } = await import('../src/i18n/localize.ts')
const render = (extra = {}, language = 'en') => renderToStaticMarkup(React.createElement(UiContext.Provider, { value: { language, t: translations[language], text: v => localizeText(v, language), date: v => formatDate(v, language) } }, React.createElement(EvidenceMap, { ...props, ...extra })))
test('missing key keeps map fallback and accessible evidence', () => {
  globalThis.mapTestKey = ''
  const html = render()
  assert.match(html, /Google Maps is not configured for this environment/)
  assert.match(html, /Business list/)
  assert.doesNotMatch(html, /data-google-map/)
})
test('loaded zero-result map includes centre and selected radius text', () => {
  globalThis.mapTestKey = 'mock-key'
  globalThis.mapTestStatus = 'LOADED'
  const html = render()
  assert.match(html, /data-google-map/)
  assert.match(html, /Analysis centre: Village/)
  assert.match(html, /Selected radius: 5 km/)
  assert.match(html, /19.2/)
})
test('backend POIs retain roles, coordinates, distance and safe display text', () => {
  const points = nearbyMapPoints(['DIRECT_COMPETITOR', 'RELATED_BUSINESS'].map((classification, index) => ({ external_type: 'node', external_id: String(index), name: '<script>unsafe</script>', latitude: 19.21, longitude: 73.12, classification, distance_km: '1.4' })))
  assert.deepEqual(points.map(p => p.role), ['DIRECT_COMPETITOR', 'RELATED_BUSINESS'])
  const html = render({ points })
  assert.match(html, /#dc2626/)
  assert.match(html, /#b45309/)
  assert.match(html, /Distance: 1.4 km/)
  assert.match(html, /OpenStreetMap \/ Overpass/)
  assert.match(html, /&lt;script&gt;/)
  assert.doesNotMatch(html, /<script>/)
})
test('loader and authentication failure leave evidence accessible', () => {
  for (const status of ['FAILED', 'AUTH_FAILURE']) {
    globalThis.mapTestStatus = status
    const html = render()
    assert.match(html, /Google Maps could not load/)
    assert.match(html, /Business list/)
  }
  globalThis.mapTestStatus = 'LOADED'
})
test('invalid location degrades locally', () => {
  assert.match(render({ latitude: NaN }), /Map location or radius is unavailable/)
})
test('consumers pass backend snapshots and map contains no discovery calls', () => {
  const market = readFileSync(new URL('../src/features/marketAnalysis/NearbyBusinessEvidence.tsx', import.meta.url), 'utf8')
  const business = readFileSync(new URL('../src/features/businessAnalysis/BusinessAnalysisPage.tsx', import.meta.url), 'utf8')
  const map = readFileSync(new URL('../src/features/marketAnalysis/MarketMap.tsx', import.meta.url), 'utf8')
  assert.match(market, /marketService.nearby/)
  assert.match(market, /radiusMeters=\{result.radius.selected_meters\}/)
  assert.match(business, /radiusMeters=\{market.radius.selected_meters\}/)
  assert.match(business, /nearbyMapPoints\(\[...market.competitors, ...market.related_businesses\]\)/)
  assert.doesNotMatch(map, /fetch\(|marketService|businessAnalysisService|PlacesService|Geocoder/)
})
test('one circle uses exact backend meters and extends its bounds with every marker', async () => {
  const { createSearchArea } = await import('../src/features/marketAnalysis/googleMapArea.ts')
  for (const radius of [1000, 5000, 10000]) {
    const circles = []
    const extended = []
    globalThis.google = { maps: { Circle: class {
      constructor(options) { circles.push(options) }
      getBounds() { return { extend: p => extended.push(p) } }
    } } }
    const positions = radius === 5000 ? [] : [{ lat: 19.21, lng: 73.12 }]
    createSearchArea({}, 19.2, 73.1, radius, positions)
    assert.equal(circles.length, 1)
    assert.equal(circles[0].radius, radius)
    assert.deepEqual(circles[0].center, { lat: 19.2, lng: 73.1 })
    assert.deepEqual(extended, positions)
  }
  delete globalThis.google
})
test('Google evidence provenance is retained in marker text and zero-result map', () => {
  globalThis.mapTestKey = 'mock-key'
  globalThis.mapTestStatus = 'LOADED'
  const points = nearbyMapPoints([{ provider: 'GOOGLE_PLACES', external_type: 'place', external_id: 'ChIJ-mock', name: 'Example', latitude:19, longitude:73, classification:'DIRECT_COMPETITOR', distance_km:'0.1' }])
  assert.equal(points[0].source, 'Google Places')
  for (const data of [points, []]) {
    const html = render({ points: data, evidenceProvider: 'GOOGLE_PLACES' })
    assert.match(html, /Google Places/)
    assert.doesNotMatch(html, /OpenStreetMap/)
  }
})

test('market map relabels all locales while preserving the evidence snapshot and proper names', () => {
  globalThis.mapTestKey = ''
  const points = nearbyMapPoints([{ provider: 'GOOGLE_PLACES', external_type: 'place', external_id: 'immutable-id', name: 'Dashboard', latitude: 19.21, longitude: 73.12, classification: 'DIRECT_COMPETITOR', distance_km: '1.4' }])
  const before = JSON.stringify(points)
  for (const language of ['en', 'hi', 'mr']) {
    const html = render({ points, centreName: 'Market Analysis' }, language)
    assert.match(html, /<strong>Dashboard<\/strong>/)
    assert.ok(html.includes('Market Analysis'))
    assert.ok(html.includes(localizeText('Analysis centre', language)))
    assert.equal(JSON.stringify(points), before)
  }
})
