export const ROTATION_MS = 6000
export type CarouselState = { index: number; revision: number }
export type CarouselAction = { type: 'next' | 'previous' | 'tick' } | { type: 'select'; index: number }
export function carouselReducer(state: CarouselState, action: CarouselAction, count: number): CarouselState {
  const index = action.type === 'select' ? action.index : state.index + (action.type === 'previous' ? -1 : 1)
  return { index: ((index % count) + count) % count, revision: state.revision + 1 }
}
export function canRotate(reducedMotion: boolean, hidden: boolean, hovered: boolean, focused: boolean, paused: boolean) {
  return !reducedMotion && !hidden && !hovered && !focused && !paused
}
export function scheduleRotation(advance: () => void, enabled: boolean, schedule = setTimeout, cancel = clearTimeout) {
  if (!enabled) return () => {}
  const timer = schedule(advance, ROTATION_MS)
  return () => cancel(timer)
}
export type ImageState = 'loading' | 'loaded' | 'error'
