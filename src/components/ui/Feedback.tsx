import { LocalizedText } from '../../i18n/LocalizedText'
import { AlertCircle, Inbox, LoaderCircle } from 'lucide-react'
import type { ReactNode } from 'react'
export function Alert({ children, tone = 'info' }: { children: ReactNode; tone?: 'info' | 'success' | 'danger' }) { return <div className={`alert alert--${tone}`} role="alert"><AlertCircle size={19} />{children}</div> }
export function LoadingState({ label = 'Loading…' }: { label?: string }) { return <div className="state"><LoaderCircle className="spin" /><p><LocalizedText value={label} /></p></div> }
export function EmptyState({ title = 'Nothing here yet', message }: { title?: string; message?: string }) { return <div className="state"><Inbox /><strong><LocalizedText value={title} /></strong>{message && <p><LocalizedText value={message} /></p>}</div> }
export function ErrorState({ message = 'Something went wrong.' }: { message?: string }) { return <div className="state state--error"><AlertCircle /><strong><LocalizedText value={"Unable to load"} /></strong><p><LocalizedText value={message} /></p></div> }
