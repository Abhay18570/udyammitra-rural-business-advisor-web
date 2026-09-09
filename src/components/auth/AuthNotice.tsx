import { LocalizedText } from '../../i18n/LocalizedText'
import { Info } from 'lucide-react'
export function AuthNotice() { return <div className="auth-notice"><Info aria-hidden="true" /><p><LocalizedText value={"Your profile information will be used to personalise business analysis and recommendations."} /></p></div> }
