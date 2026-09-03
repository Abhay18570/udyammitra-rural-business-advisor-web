import type { ReactNode } from 'react'
export function Badge({ children, tone = 'navy' }: { children: ReactNode; tone?: 'navy' | 'green' | 'orange' }) { return <span className={`badge badge--${tone}`}>{children}</span> }
