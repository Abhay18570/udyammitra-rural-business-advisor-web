import { useUi as useTextUi } from '../../i18n/uiContextValue'
import { LocalizedText } from '../../i18n/LocalizedText'
import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { AuthField, PasswordField } from '../../components/auth/AuthFields'
import { AuthNotice } from '../../components/auth/AuthNotice'
import { Button } from '../../components/ui/Button'
import { loginSchema, type LoginFormData } from '../../features/auth/authSchemas'
import { useAuth } from '../../context/authContextValue'
import { getApiErrorMessage } from '../../services/apiError'

export function LoginPage() {
  const { text: textUi } = useTextUi()

  const [serverError, setServerError] = useState('')
  const { login } = useAuth(); const navigate = useNavigate(); const location = useLocation()
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginFormData>({ resolver: zodResolver(loginSchema), defaultValues: { identifier: '', password: '', rememberMe: false } })
  const onSubmit = async (values: LoginFormData) => { setServerError(''); try { await login(values); const destination = (location.state as { from?: string } | null)?.from ?? '/dashboard'; navigate(destination, { replace: true }) } catch (error) { setServerError(getApiErrorMessage(error, 'Unable to sign in. Please try again.')) } }
  return <section className="auth-card"><span className="eyebrow"><LocalizedText value={"Account access"} /></span><h2><LocalizedText value={"Welcome Back"} /></h2><p><LocalizedText value={"Sign in to continue your business planning journey."} /></p><form onSubmit={handleSubmit(onSubmit)} noValidate><AuthField id="login-identifier" label={textUi("Email or Mobile Number")} autoComplete="username" placeholder={textUi("Enter email or mobile number")} error={errors.identifier?.message} {...register('identifier')} /><PasswordField id="login-password" label={textUi("Password")} autoComplete="current-password" placeholder={textUi("Enter your password")} error={errors.password?.message} {...register('password')} /><div className="form-options"><label className="choice"><input type="checkbox" {...register('rememberMe')} /><span><LocalizedText value={"Remember Me"} /></span></label><Link to="/forgot-password"><LocalizedText value={"Forgot Password?"} /></Link></div>{serverError && <p className="integration-message integration-message--error" role="alert"><LocalizedText value={serverError} /></p>}<Button type="submit" disabled={isSubmitting}><LocalizedText value={isSubmitting ? 'Signing in…' : 'Login'} /></Button></form><AuthNotice /><p className="auth-link"><LocalizedText value={"New to UdyamMitra? "} /><Link to="/register"><LocalizedText value={"Create Account"} /></Link></p></section>
}
