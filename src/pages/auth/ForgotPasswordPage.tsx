import { useUi as useTextUi } from '../../i18n/uiContextValue'
import { LocalizedText } from '../../i18n/LocalizedText'
import { zodResolver } from '@hookform/resolvers/zod'
import { ArrowLeft } from 'lucide-react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'
import { AuthField } from '../../components/auth/AuthFields'
import { Button } from '../../components/ui/Button'
import { forgotPasswordSchema, type ForgotPasswordFormData } from '../../features/auth/authSchemas'
export function ForgotPasswordPage() {
  const { text: textUi } = useTextUi()
 const [submitted, setSubmitted] = useState(false); const { register, handleSubmit, formState: { errors } } = useForm<ForgotPasswordFormData>({ resolver: zodResolver(forgotPasswordSchema), defaultValues: { identifier: '' } }); return <section className="auth-card"><span className="eyebrow"><LocalizedText value={"Account recovery"} /></span><h2><LocalizedText value={"Forgot Your Password?"} /></h2><p><LocalizedText value={"Enter your registered email address or mobile number."} /></p><form onSubmit={handleSubmit(() => setSubmitted(true))} noValidate><AuthField id="recovery-identifier" label={textUi("Email or Mobile Number")} autoComplete="username" placeholder={textUi("Enter email or mobile number")} error={errors.identifier?.message} {...register('identifier')} />{submitted && <p className="integration-message" role="status"><LocalizedText value={"Password recovery will be connected in the backend integration phase. No message has been sent."} /></p>}<Button type="submit"><LocalizedText value={"Continue"} /></Button></form><p className="auth-link"><Link to="/login"><ArrowLeft size={15} aria-hidden="true" /><LocalizedText value={" Back to Login"} /></Link></p></section> }
