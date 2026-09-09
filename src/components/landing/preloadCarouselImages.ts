import { carouselSlides, landingImageFolder } from '../../data/landingPortal'
import type { ImageState } from './carouselState'

/** The browser cache shares these requests with the actual slide image elements. */
export function preloadCarouselImages(onSettled: (id: string, state: ImageState) => void, ImageConstructor = Image) {
  let cancelled = false
  const images = carouselSlides.slice(1).map(slide => {
    const image = new ImageConstructor()
    image.fetchPriority = 'low'
    image.onload = () => { if (!cancelled) onSettled(slide.id, 'loaded') }
    image.onerror = () => { if (!cancelled) onSettled(slide.id, 'error') }
    image.src = landingImageFolder + slide.image
    return image
  })
  return () => {
    cancelled = true
    images.forEach(image => { image.onload = null; image.onerror = null })
  }
}
