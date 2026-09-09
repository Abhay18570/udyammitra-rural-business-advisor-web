import { LocalizedText } from '../../i18n/LocalizedText'
import type { InputHTMLAttributes, SelectHTMLAttributes } from 'react'
export function Input({ label, id, ...props }: InputHTMLAttributes<HTMLInputElement> & { label: string; id: string }) { return <label className="field" htmlFor={id}><span><LocalizedText value={label} /></span><input id={id} {...props} /></label> }
export function Select({ label, id, children, ...props }: SelectHTMLAttributes<HTMLSelectElement> & { label: string; id: string }) { return <label className="field" htmlFor={id}><span><LocalizedText value={label} /></span><select id={id} {...props}>{children}</select></label> }
export function Checkbox({ label, id, ...props }: InputHTMLAttributes<HTMLInputElement> & { label: string; id: string }) { return <label className="choice" htmlFor={id}><input id={id} type="checkbox" {...props} /><span><LocalizedText value={label} /></span></label> }
export function Radio({ label, id, ...props }: InputHTMLAttributes<HTMLInputElement> & { label: string; id: string }) { return <label className="choice" htmlFor={id}><input id={id} type="radio" {...props} /><span><LocalizedText value={label} /></span></label> }
