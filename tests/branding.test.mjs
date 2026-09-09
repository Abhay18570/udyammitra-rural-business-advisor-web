import './tsxLoader.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFileSync, existsSync } from 'node:fs'
import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
const { UdyamMitraLogo, udyamMitraLogoPath, udyamMitraTransparentLogoPath } = await import('../src/components/common/UdyamMitraLogo.tsx')
const { PublicHeader } = await import('../src/components/layout/PublicHeader.tsx')
const { AuthLayout } = await import('../src/layouts/AuthLayout.tsx')
const { UserDashboardLayout } = await import('../src/layouts/UserDashboardLayout.tsx')
const { LandingFooter } = await import('../src/components/landing/LandingFooter.tsx')
const { Footer } = await import('../src/components/layout/Footer.tsx')
const { UiContext } = await import('../src/i18n/uiContextValue.ts')
const { AuthContext } = await import('../src/context/authContextValue.ts')
const { translations } = await import('../src/i18n/translations.ts')
const { localizeText } = await import('../src/i18n/localize.ts')
const render = (Component, language = 'en', props = {}) => renderToStaticMarkup(
  React.createElement(AuthContext.Provider, { value: { user: null, isAuthenticated: false } },
    React.createElement(UiContext.Provider, { value: { language, t: translations[language], text: v => localizeText(v, language), setLanguage() {}, setFontScale() {} } },
      React.createElement(MemoryRouter, null, React.createElement(Component, props)))))
const assertLogo = (html, transparent = false) => {
  assert.ok(html.includes(`src="${transparent ? udyamMitraTransparentLogoPath : udyamMitraLogoPath}"`))
  assert.doesNotMatch(html, /lucide-sprout|lucide-leaf|tests\/logo/)
}

test('production asset is the exact supplied JPEG, with no test-folder duplicate', () => {
  const file = readFileSync(new URL('../public' + udyamMitraLogoPath, import.meta.url))
  assert.equal(createHash('sha256').update(file).digest('hex'), '58691f264361b5975050cdbf561c4901fb5b5324622aa29b0895d649410cf66b')
  assert.equal(existsSync(new URL('./logo/UdyamMitra_Logo.jpeg', import.meta.url)), false)
  assert.ok(readFileSync(new URL('../index.html', import.meta.url), 'utf8').includes(`type="image/jpeg" href="${udyamMitraLogoPath}"`))
})

test('reusable logo has an accessible standalone name and decorative mode beside brand text', () => {
  const standalone = render(UdyamMitraLogo)
  assertLogo(standalone)
  assert.match(standalone, /alt="UdyamMitra"/)
  assert.match(standalone, /loading="eager"/)
  assert.match(standalone, /width="\d+" height="\d+"/)
  const decorative = render(UdyamMitraLogo, 'en', { decorative: true })
  assert.match(decorative, /alt="" aria-hidden="true"/)
  for (const size of ['small', 'medium', 'large']) assertLogo(render(UdyamMitraLogo, 'en', { size }))
})

for (const language of ['en', 'hi', 'mr']) test(`public, auth and footer branding use the logo in ${language}`, () => {
  assertLogo(render(PublicHeader, language, { landing: true }))
  // Login, Register and Forgot Password all render inside this unchanged shared layout.
  assertLogo(render(AuthLayout, language), true)
  assertLogo(render(LandingFooter, language), true)
  assertLogo(render(Footer, language), true)
})

test('expanded and persisted collapsed dashboard sidebars render the image and retain collapse controls', () => {
  const prior = Object.getOwnPropertyDescriptor(globalThis, 'localStorage')
  try {
    for (const collapsed of [false, true]) {
      Object.defineProperty(globalThis, 'localStorage', { configurable: true, value: { getItem: () => String(collapsed) } })
      const html = render(UserDashboardLayout)
      assertLogo(html, true)
      assert.equal(html.includes('dashboard-layout dashboard-layout--collapsed'), collapsed)
      assert.ok(html.includes(`aria-label="${collapsed ? 'Expand' : 'Collapse'} sidebar"`))
      assert.ok(html.includes(`aria-expanded="${!collapsed}" aria-controls="dashboard-sidebar"`))
      assert.match(html, /title="UdyamMitra home"/)
      assert.match(html, /aria-label="Open sidebar"/)
    }
  } finally {
    if (prior) Object.defineProperty(globalThis, 'localStorage', prior)
    else delete globalThis.localStorage
  }
})

test('logo styling preserves its aspect ratio and existing collapsed text hiding', () => {
  const css = readFileSync(new URL('../src/responsive.css', import.meta.url), 'utf8')
  assert.match(css, /\.udyammitra-logo\s*\{[^}]*object-fit: contain/)
  assert.match(css, /\.udyammitra-logo\s*\{[^}]*aspect-ratio: 1/)
  assert.match(css, /\.dashboard-layout--collapsed \.sidebar \.brand > span:not\(\.brand__mark\)\s*\{\s*display: none/)
  assert.doesNotMatch(css, /\.udyammitra-logo\s*\{[^}]*(filter:|object-fit: cover)/)
})


test('explicit transparent variant uses PNG without changing default navbar image', () => {
  assertLogo(render(UdyamMitraLogo))
  const transparent = render(UdyamMitraLogo, 'en', { variant: 'transparent' })
  assertLogo(transparent, true)
  assert.match(transparent, /udyammitra-logo--transparent/)
  assert.match(transparent, /alt="UdyamMitra"/)
  assertLogo(render(PublicHeader, 'en', { landing: true }))
  const png = readFileSync(new URL('../public' + udyamMitraTransparentLogoPath, import.meta.url))
  assert.equal(png.subarray(1, 4).toString(), 'PNG')
  assert.equal(png[25], 6, 'RGBA image includes an alpha channel')
  const css = readFileSync(new URL('../src/responsive.css', import.meta.url), 'utf8')
  assert.match(css, /\.udyammitra-logo--transparent \{ background: transparent/)
  assert.match(css, /\.brand--inverse \.brand__mark \{ background: transparent/)
})
