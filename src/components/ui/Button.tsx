import type { ButtonHTMLAttributes, MouseEventHandler, ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { cn } from '../../utils/cn'
type Variant = 'primary' | 'secondary' | 'outline' | 'success' | 'danger' | 'ghost'
export function Button({ variant = 'primary', className, ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) { return <button className={cn('button', `button--${variant}`, className)} {...props} /> }
export function ButtonLink({ to, variant = 'primary', className, children, onClick }: { to: string; variant?: Variant; className?: string; children: ReactNode; onClick?: MouseEventHandler<HTMLAnchorElement> }) { return <Link to={to} className={cn('button', `button--${variant}`, className)} onClick={onClick}>{children}</Link> }
