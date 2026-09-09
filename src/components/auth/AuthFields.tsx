import { useUi as useTextUi } from '../../i18n/uiContextValue'
import { LocalizedText } from '../../i18n/LocalizedText'
import { Eye, EyeOff } from 'lucide-react'
import { useState, type InputHTMLAttributes, type SelectHTMLAttributes } from 'react'

type FieldProps = InputHTMLAttributes<HTMLInputElement> & { label: string; error?: string }
export function AuthField({ label, id, error, ...props }: FieldProps) { return <div className="auth-field"><label htmlFor={id}><LocalizedText value={label} /></label><input id={id} aria-invalid={Boolean(error)} aria-describedby={error ? `${id}-error` : undefined} {...props} />{error && <span className="field-error" id={`${id}-error`} role="alert"><LocalizedText value={error} /></span>}</div> }
export function PasswordField({ label, id, error, ...props }: FieldProps) {
  const { text: textUi } = useTextUi()
 const [visible, setVisible] = useState(false); return <div className="auth-field"><label htmlFor={id}><LocalizedText value={label} /></label><div className="password-input"><input id={id} type={visible ? 'text' : 'password'} aria-invalid={Boolean(error)} aria-describedby={error ? `${id}-error` : undefined} {...props} /><button type="button" onClick={() => setVisible(value => !value)} aria-label={`${textUi(visible ? 'Hide' : 'Show')} ${textUi(label)}`}>{visible ? <EyeOff aria-hidden="true" /> : <Eye aria-hidden="true" />}</button></div>{error && <span className="field-error" id={`${id}-error`} role="alert"><LocalizedText value={error} /></span>}</div> }
export function AuthSelect({ label, id, error, children, ...props }: SelectHTMLAttributes<HTMLSelectElement> & { label: string; error?: string }) { return <div className="auth-field"><label htmlFor={id}><LocalizedText value={label} /></label><select id={id} aria-invalid={Boolean(error)} aria-describedby={error ? `${id}-error` : undefined} {...props}>{children}</select>{error && <span className="field-error" id={`${id}-error`} role="alert"><LocalizedText value={error} /></span>}</div> }
