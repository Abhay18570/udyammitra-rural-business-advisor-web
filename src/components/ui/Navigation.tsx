import { useUi as useTextUi } from '../../i18n/uiContextValue'
import { LocalizedText } from '../../i18n/LocalizedText'
import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
export function Breadcrumbs({ items }: { items: { label: string; to?: string }[] }) {
  const { text: textUi } = useTextUi()
 return <nav className="breadcrumbs" aria-label={textUi("Breadcrumb")}><ol>{items.map((item, i) => <li key={item.label}>{item.to ? <Link to={item.to}><LocalizedText value={item.label} /></Link> : <span aria-current="page"><LocalizedText value={item.label} /></span>}{i < items.length - 1 && <span>/</span>}</li>)}</ol></nav> }
export function Tabs({ tabs, active }: { tabs: string[]; active: string }) { return <div className="tabs" role="tablist">{tabs.map(tab => <button key={tab} role="tab" aria-selected={tab === active}><LocalizedText value={tab} /></button>)}</div> }
export function Progress({ value, label }: { value: number; label: string }) { return <div className="progress"><div><span><LocalizedText value={label} /></span><strong>{value}%</strong></div><progress value={value} max="100" /></div> }
export function PageHeading({ eyebrow, title, description, actions }: { eyebrow?: string; title: string; description?: string; actions?: ReactNode }) { return <div className="page-heading"><div>{eyebrow && <span className="eyebrow"><LocalizedText value={eyebrow} /></span>}<h1><LocalizedText value={title} /></h1>{description && <p><LocalizedText value={description} /></p>}</div>{actions}</div> }
export function SectionHeading({ eyebrow, title, description, centered = false }: { eyebrow?: string; title: string; description?: string; centered?: boolean }) { return <div className={`section-heading ${centered ? 'section-heading--centered' : ''}`}>{eyebrow && <span className="eyebrow"><LocalizedText value={eyebrow} /></span>}<h2><LocalizedText value={title} /></h2>{description && <p><LocalizedText value={description} /></p>}</div> }
