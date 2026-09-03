import type { HTMLAttributes, ReactNode } from 'react'
import { cn } from '../../utils/cn'
export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) { return <div className={cn('card', className)} {...props} /> }
export function StatCard({ label, value, icon }: { label: string; value: string; icon?: ReactNode }) { return <Card className="stat-card"><span>{icon}</span><strong>{value}</strong><small>{label}</small></Card> }
