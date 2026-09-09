import { useEffect, type RefObject } from 'react'

/** Progressive enhancement: no observer, reduced motion, or JS failure leaves content visible. */
export function observeReveals(root: HTMLElement, Observer: typeof IntersectionObserver | undefined, reducedMotion: boolean) {
  if (!Observer || reducedMotion) return () => {}
  const targets = root.querySelectorAll<HTMLElement>('[data-reveal]')
  const seen = new WeakSet<Element>()
  const observer = new Observer(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting || seen.has(entry.target)) continue
      seen.add(entry.target)
      entry.target.classList.add('portal-revealed')
      observer.unobserve(entry.target)
    }
  }, { threshold: 0.08 })
  targets.forEach(target => {
    // Related items share their parent's stagger; headings and footer start immediately.
    const siblings = target.parentElement?.querySelectorAll(':scope > [data-reveal]')
    const index = siblings ? Array.from(siblings).indexOf(target) : 0
    target.style.setProperty('--reveal-delay', `${Math.min(Math.max(index, 0), 5) * 60}ms`)
    observer.observe(target)
  })
  return () => {
    observer.disconnect()
    targets.forEach(target => {
      target.classList.remove('portal-revealed')
      target.style.removeProperty('--reveal-delay')
    })
  }
}

export function useRevealOnScroll(root: RefObject<HTMLDivElement | null>, enabled: boolean) {
  useEffect(() => {
    if (!enabled || !root.current) return
    return observeReveals(root.current, window.IntersectionObserver,
      window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false)
  }, [root, enabled])
}
