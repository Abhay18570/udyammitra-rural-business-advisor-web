import { UdyamMitraLogo } from '../common/UdyamMitraLogo'
import { useEffect, useReducer, useRef, useState } from 'react'
import { ArrowLeft, ArrowRight, Pause, Play } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useUi } from '../../i18n/uiContextValue'
import { landingMessages as m } from '../../i18n/landingMessages'
import { carouselSlides, landingImageFolder, type CarouselSlide } from '../../data/landingPortal'
import { canRotate, carouselReducer, scheduleRotation, type ImageState } from './carouselState'

export function HeroSlide({ slide, active, first, loadImage, imageState, onImageState }: {
  slide: CarouselSlide; active: boolean; first: boolean; loadImage: boolean
  imageState: ImageState; onImageState: (state: ImageState) => void
}) {
  const { text } = useUi()
  const image = useRef<HTMLImageElement>(null)
  useEffect(() => {
    if (image.current?.complete && image.current.naturalWidth > 0) onImageState('loaded')
  }, [loadImage, onImageState])
  return <article className={`portal-slide portal-slide--${slide.id} ${active ? 'is-active' : ''}`} aria-hidden={!active} inert={!active}
    role="group" aria-roledescription={text(m.slide.en)} aria-label={text(slide.eyebrow)}>
    <div className="portal-art" aria-hidden="true"><div className="portal-art__sun" /><div className="portal-art__field" /><div className="portal-art__seal"><UdyamMitraLogo variant="transparent" size="large" decorative /><span>UdyamMitra</span><small>{text(m.fallback.en)}</small></div></div>
    {loadImage && imageState !== 'error' && <img ref={image} className={`portal-photo ${imageState === 'loaded' ? 'is-loaded' : ''}`} src={landingImageFolder + slide.image} alt={text(slide.alt)}
      fetchPriority={first ? 'high' : 'low'} loading="eager" decoding="async" onLoad={() => onImageState('loaded')} onError={() => onImageState('error')} />}
    <div className="portal-overlay" />
    {active && loadImage && imageState === 'loading' && <span className="portal-image-loading" role="status"><span className="sr-only">{text(m.loading.en)}</span></span>}
    <div className="portal-container portal-slide__body">
      <div className="portal-slide__copy"><span className="portal-eyebrow"><i />{text(slide.eyebrow)}</span>
        {first ? <h1>{text(slide.title)}</h1> : <h2>{text(slide.title)}</h2>}
        <p>{text(slide.description)}</p><div className="portal-actions">
          {slide.comingSoon ? <span className="portal-coming">{text(m.soon.en)}</span> : <Link className="portal-button" to={slide.to}>{text(slide.action)}<ArrowRight aria-hidden="true" size={18} /></Link>}
          <a className="portal-button portal-button--glass" href="#how-it-works">{text(m.how.en)}</a>
        </div>
      </div>
    </div>
  </article>
}

export function CarouselControls({ index, paused, onPrevious, onNext, onSelect, onPause, text }: {
  text: (value: string) => string; index: number; paused: boolean; onPrevious: () => void; onNext: () => void; onSelect: (index: number) => void; onPause: () => void
}) {
  return <div className="portal-carousel-controls">
    <button onClick={onPrevious} aria-label={text(m.previous.en)}><ArrowLeft aria-hidden="true" size={19} /></button>
    <div className="portal-dots">{carouselSlides.map((slide, i) => <button key={slide.id} aria-label={`${text(m.slide.en)} ${i + 1}: ${text(slide.eyebrow)}`} aria-current={i === index ? 'true' : undefined} onClick={() => onSelect(i)}><span /></button>)}</div>
    <button onClick={onNext} aria-label={text(m.next.en)}><ArrowRight aria-hidden="true" size={19} /></button>
    <button onClick={onPause} aria-label={text(paused ? m.play.en : m.pause.en)} aria-pressed={paused}>{paused ? <Play aria-hidden="true" size={17} /> : <Pause aria-hidden="true" size={17} />}</button>
  </div>
}

export function HeroCarousel() {
  const { text } = useUi()
  const [state, dispatch] = useReducer((state: { index: number; revision: number }, action: Parameters<typeof carouselReducer>[1]) => carouselReducer(state, action, carouselSlides.length), { index: 0, revision: 0 })
  const [reducedMotion, setReducedMotion] = useState(() => typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches)
  const [hidden, setHidden] = useState(() => typeof document !== 'undefined' && document.hidden)
  const [hovered, setHovered] = useState(false)
  const [focused, setFocused] = useState(false)
  const [paused, setPaused] = useState(false)
  const [images, setImages] = useState<Record<string, ImageState>>({})
  const touch = useRef<{ x: number; y: number } | null>(null)
  useEffect(() => {
    const media = window.matchMedia('(prefers-reduced-motion: reduce)')
    const updateMotion = () => setReducedMotion(media.matches)
    const updateVisibility = () => setHidden(document.hidden)
    media.addEventListener('change', updateMotion)
    document.addEventListener('visibilitychange', updateVisibility)
    return () => { media.removeEventListener('change', updateMotion); document.removeEventListener('visibilitychange', updateVisibility) }
  }, [])
  // Warm only the next image, after the current image has settled. Retain visited images.
  const currentImage = images[carouselSlides[state.index].id]
  const rotating = canRotate(reducedMotion, hidden, hovered, focused, paused)
  useEffect(() => scheduleRotation(() => dispatch({ type: 'tick' }), rotating), [rotating, state.revision])
  return <section className="portal-carousel" tabIndex={0} role="region" aria-roledescription={text(m.carousel.en)} aria-label={text(m.carousel.en)}
    onMouseEnter={() => setHovered(true)} onMouseLeave={() => setHovered(false)}
    onFocusCapture={() => setFocused(true)} onBlurCapture={event => { if (!event.currentTarget.contains(event.relatedTarget)) setFocused(false) }}
    onKeyDown={event => {
      if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') { event.preventDefault(); event.currentTarget.focus(); dispatch({ type: event.key === 'ArrowRight' ? 'next' : 'previous' }) }
    }}
    onTouchStart={event => { touch.current = { x: event.touches[0].clientX, y: event.touches[0].clientY } }}
    onTouchCancel={() => { touch.current = null }}
    onTouchEnd={event => {
      if (!touch.current) return
      const dx = event.changedTouches[0].clientX - touch.current.x
      const dy = event.changedTouches[0].clientY - touch.current.y
      if (Math.abs(dx) > 55 && Math.abs(dx) > Math.abs(dy) * 1.5) dispatch({ type: dx < 0 ? 'next' : 'previous' })
      touch.current = null
    }}>
    <div className="portal-slides">{carouselSlides.map((slide, i) => <HeroSlide key={slide.id} slide={slide} active={i === state.index} first={i === 0}
      loadImage={images[slide.id] !== undefined || i === state.index || (!hidden && currentImage !== undefined && currentImage !== 'loading' && i === (state.index + 1) % carouselSlides.length)} imageState={images[slide.id] ?? 'loading'}
      onImageState={value => setImages(previous => previous[slide.id] === value ? previous : { ...previous, [slide.id]: value })} />)}</div>
    <div className="portal-container portal-carousel-bottom"><span className="portal-carousel-brand">UdyamMitra <i /> {String(state.index + 1).padStart(2, '0')} / 05</span>
      <CarouselControls text={text} index={state.index} paused={paused} onPrevious={() => dispatch({ type: 'previous' })} onNext={() => dispatch({ type: 'next' })} onSelect={index => dispatch({ type: 'select', index })} onPause={() => setPaused(value => !value)} />
    </div>
    <span className="sr-only" aria-live={rotating ? 'off' : 'polite'} aria-atomic="true">{text(m.slide.en)} {state.index + 1}: {text(carouselSlides[state.index].eyebrow)}</span>
  </section>
}
