import test from 'node:test'
import assert from 'node:assert/strict'
import { initialNearbyState, nearbyReducer, proposedBusinessDefault, selectedCircleMeters } from '../src/features/marketAnalysis/nearbyState.ts'

const evidence = (radius = 5, slug = 'tailoring-alteration') => ({ business: { slug }, radius: { selected_km: radius, selected_meters: radius * 1000 } })
test('radius defaults to five and missing proposed selection stays empty', () => {
  assert.equal(initialNearbyState.radius, 5)
  assert.equal(initialNearbyState.slug, '')
  assert.deepEqual(proposedBusinessDefault(null, [{ id: '1', slug: 'tailor' }]), { slug: '', unavailable: false })
})
test('saved business resolves by catalog ID and unavailable choices stay empty', () => {
  assert.deepEqual(proposedBusinessDefault('1', [{ id: '1', slug: 'tailor' }]), { slug: 'tailor', unavailable: false })
  assert.deepEqual(proposedBusinessDefault('inactive', [{ id: '1', slug: 'tailor' }]), { slug: '', unavailable: true })
})
test('radius preserves loaded evidence; legacy business selection clears it', () => {
  const state = { slug: 'tailoring-alteration', radius: 5, result: evidence() }
  assert.equal(nearbyReducer(state, { type: 'radius', value: 8 }).result, state.result)
  assert.equal(nearbyReducer(state, { type: 'business', value: 'kirana-general-store' }).result, null)
  assert.equal(state.result.radius.selected_km, 5)
})
test('late incompatible evidence cannot replace current selected state', () => {
  const state = { slug: 'tailoring-alteration', radius: 8, result: null }
  assert.equal(nearbyReducer(state, { type: 'result', value: evidence(5) }).result, null)
  assert.equal(nearbyReducer(state, { type: 'result', value: evidence(8, 'other') }).result, null)
  assert.equal(nearbyReducer(state, { type: 'result', value: evidence(8) }).result.radius.selected_km, 8)
})
test('real map receives exactly one circle for the returned selected radius', () => {
  assert.deepEqual(selectedCircleMeters(evidence(3)), [3000])
  assert.deepEqual(selectedCircleMeters(evidence(8)), [8000])
})
