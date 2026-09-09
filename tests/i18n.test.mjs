import './tsxLoader.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
const { translations } = await import('../src/i18n/translations.ts')
const { messages } = await import('../src/i18n/messages.ts')
const { runtimeMessages } = await import('../src/i18n/runtimeMessages.ts')
const { enumMessages } = await import('../src/i18n/statusMessages.ts')
const { localizeText, readLanguage, saveLanguage, formatDate } = await import('../src/i18n/localize.ts')
const { LocalizedText } = await import('../src/i18n/LocalizedText.tsx')
const { UiContext } = await import('../src/i18n/uiContextValue.ts')
const { formatINR } = await import('../src/utils/inr.ts')
function leaves(object, prefix = '', result = {}) {
  for (const [key, value] of Object.entries(object)) {
    if (typeof value === 'string') result[prefix + key] = value
    else leaves(value, prefix + key + '.', result)
  }
  return result
}
function parity(locales) {
  const base = leaves(locales.en)
  for (const locale of ['hi', 'mr']) {
    const translated = leaves(locales[locale])
    assert.deepEqual(Object.keys(translated).sort(), Object.keys(base).sort())
    for (const key of Object.keys(base)) {
      assert.ok(translated[key].trim(), key)
      assert.deepEqual((translated[key].match(/\{\d+\}/g) || []).sort(), (base[key].match(/\{\d+\}/g) || []).sort(), key)
    }
  }
}
test('all original locale keys and every supplemental message have parity', () => {
  parity(translations)
  for (const group of [...Object.values(messages), ...Object.values(runtimeMessages), enumMessages]) {
    for (const row of Object.values(group)) parity({ en: { value: row.en }, hi: { value: row.hi }, mr: { value: row.mr } })
  }
})
test('missing known key is rejected', () => assert.throws(() => parity({ en: { save: 'Save' }, hi: {}, mr: { save: 'जतन करा' } })))
for (const language of ['en', 'hi', 'mr']) test(`${language} renders shared and authenticated feature labels`, () => {
  for (const label of ['Dashboard', 'Market Analysis', 'Financial Plan', 'Business Analysis', 'Save & Continue', 'Government Schemes', 'Profile', 'Settings', 'Login']) {
    const expected = localizeText(label, language)
    if (language !== 'en') assert.notEqual(expected, label, label)
    const html = renderToStaticMarkup(React.createElement(UiContext.Provider, { value: { text: v => localizeText(v, language) } }, React.createElement(LocalizedText, { value: label })))
    assert.ok(html.length > 0)
    assert.ok(expected.length > 0)
  }
})
test('explicit language persists; unavailable and invalid storage fall back safely', () => {
  const data = new Map(); const storage = { getItem: k => data.get(k), setItem: (k,v) => data.set(k,v) }
  saveLanguage('mr', storage); assert.equal(readLanguage(storage), 'mr')
  storage.setItem('udyammitra-language', 'xx'); assert.equal(readLanguage(storage), 'en')
  assert.equal(readLanguage({ getItem() { throw Error('disabled') } }), 'en')
})
test('API enums and validation messages translate without changing identifiers', () => {
  for (const value of ['ELIGIBLE', 'OUT_OF_SUPPORTED_RANGE', 'SELF_REPORTED', 'VERY_STRONG', 'Email is required']) for (const language of ['hi','mr']) assert.notEqual(localizeText(value, language), value)
})
test('currency retains Indian grouping and dates retain Arabic numerals', () => {
  assert.equal(formatINR('140000'), '₹1,40,000'); assert.equal(formatINR('5000000'), '₹50,00,000')
  for (const locale of ['en','hi','mr']) assert.match(formatDate('2026-09-08T12:00:00Z', locale), /2026/)
})
test('unknown messages retain safe text and template captures preserve external names', () => {
  assert.equal(localizeText('Unrecognized backend response', 'hi'), 'Unrecognized backend response')
  assert.ok(localizeText('Analysis centre: My Shop', 'mr').includes('My Shop'))
})

test('stable backend error codes use localized known messages; unknown details survive', async () => {
  const { getApiErrorMessage } = await import('../src/services/apiError.ts')
  const known = getApiErrorMessage({ isAxiosError: true, response: { data: { detail: { code: 'PROVIDER_TIMEOUT', message: 'technical detail' } } } }, 'fallback')
  assert.notEqual(known, 'technical detail')
  assert.notEqual(localizeText(known, 'hi'), known)
  assert.equal(getApiErrorMessage({ isAxiosError: true, response: { data: { detail: { code: 'UNKNOWN', message: 'new response' } } } }, 'fallback'), 'new response')
})

test('profile localization preserves user-entered names even when they match UI labels', async () => {
  const { MemoryRouter } = await import('react-router-dom')
  const { ProfileSnapshot } = await import('../src/features/dashboard/ProfileSnapshot.tsx')
  const profile = { skills: [{ name: 'Other', otherDescription: 'Dashboard' }], resources: [], hasExistingBusiness: true, existingBusiness: { businessName: 'Settings' }, village: 'Profile', ownCapital: '140000', loanRequired: '50000' }
  const before = JSON.stringify(profile)
  for (const language of ['en', 'hi', 'mr']) {
    const html = renderToStaticMarkup(React.createElement(UiContext.Provider, { value: { text: v => localizeText(v, language) } }, React.createElement(MemoryRouter, null, React.createElement(ProfileSnapshot, { profile }))))
    assert.match(html, /<dd>Settings<\/dd>/)
    assert.match(html, /<dd>Dashboard<\/dd>/)
    assert.match(html, /<dd>Profile<\/dd>/)
    assert.equal(JSON.stringify(profile), before)
  }
})

test('known literal display labels cannot silently fall back to English', async () => {
  const { readdirSync, readFileSync } = await import('node:fs')
  const { default: ts } = await import('typescript')
  const intentional = new Set(['English', 'Kirana / General Store', 'Mobile Repair & Accessories', 'OpenStreetMap / Overpass', 'UdyamMitra'])
  function walk(directory) {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const path = directory + '/' + entry.name
      if (entry.isDirectory()) { walk(path); continue }
      if (!path.endsWith('.tsx')) continue
      const ast = ts.createSourceFile(path, readFileSync(path, 'utf8'), ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX)
      function visit(node) {
        if (ts.isJsxSelfClosingElement(node) && node.tagName.getText(ast) === 'LocalizedText') {
          const attr = node.attributes.properties.find(a => a.name?.getText(ast) === 'value')
          const value = attr?.initializer
          const expression = value && ts.isJsxExpression(value) ? value.expression : value
          if (expression && ts.isStringLiteral(expression) && /[a-zA-Z]{2}/.test(expression.text) && !intentional.has(expression.text.trim())) {
            for (const language of ['hi', 'mr']) assert.notEqual(localizeText(expression.text, language), expression.text, path + ': ' + expression.text)
          }
        }
        ts.forEachChild(node, visit)
      }
      visit(ast)
    }
  }
  walk(new URL('../src', import.meta.url).pathname)
})

test('saved preference applies only to its account and cannot override a newer explicit choice', async () => {
  const { canApplySavedLanguage } = await import('../src/i18n/localize.ts')
  assert.equal(canApplySavedLanguage(false, 0, 0, 'a', 'a'), true)
  assert.equal(canApplySavedLanguage(false, 0, 1, 'a', 'a'), false)
  assert.equal(canApplySavedLanguage(false, 0, 0, 'a', 'b'), false)
  assert.equal(canApplySavedLanguage(true, 0, 0, 'a', 'a'), false)
})
test('authenticated preference save preserves onboarding step and sends no form or analysis data', async () => {
  const { apiClient } = await import('../src/services/apiClient.ts')
  const { profileService } = await import('../src/services/profileService.ts')
  const originalGet = profileService.get, originalPut = apiClient.put
  const writes = []
  try {
    profileService.get = async () => ({ onboardingStep: 4, preferredLanguage: 'hi', fullName: 'Settings' })
    apiClient.put = async (path, payload) => { writes.push({ path, payload }); return { data: {} } }
    await profileService.setPreferredLanguage('mr')
    assert.deepEqual(writes, [{ path: '/profile', payload: { preferred_language: 'mr', onboarding_step: 4 } }])
  } finally { profileService.get = originalGet; apiClient.put = originalPut }
})

test('analysis loaders and component identity do not depend on presentation language', async () => {
  const { readFileSync } = await import('node:fs')
  const { default: ts } = await import('typescript')
  for (const file of ['features/marketAnalysis/NearbyBusinessEvidence.tsx', 'features/marketAnalysis/MarketAnalysisPage.tsx', 'features/financial/FinancialPlanPage.tsx', 'features/financial/SchemeEligibilityPanel.tsx', 'features/businessAnalysis/BusinessAnalysisPage.tsx', 'features/onboarding/OnboardingPage.tsx']) {
    const source = readFileSync(new URL('../src/' + file, import.meta.url), 'utf8')
    const ast = ts.createSourceFile(file, source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX)
    function visit(node) {
      if (ts.isCallExpression(node) && ['useEffect','useMemo','useCallback'].includes(node.expression.getText(ast)) && node.arguments[1]) assert.doesNotMatch(node.arguments[1].getText(ast), /\b(language|labels|textUi|t)\b/, file)
      if (ts.isJsxAttribute(node) && node.name.getText(ast) === 'key') assert.doesNotMatch(node.initializer?.getText(ast) || '', /\blanguage\b/, file)
      ts.forEachChild(node, visit)
    }
    visit(ast)
  }
})
