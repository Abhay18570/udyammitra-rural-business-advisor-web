import { useUi as useTextUi } from '../../i18n/uiContextValue'
import { LocalizedText } from '../../i18n/LocalizedText'
import { UdyamMitraLogo } from './UdyamMitraLogo'
import { Link } from 'react-router-dom'
import { cn } from '../../utils/cn'
export function Brand({ inverse = false, preserveName = false }: { inverse?: boolean; preserveName?: boolean }) {
  const { text: textUi } = useTextUi()
 return <Link to="/" className={cn('brand', inverse && 'brand--inverse')} aria-label={textUi("UdyamMitra home")} title={textUi("UdyamMitra home")}><span className="brand__mark" aria-hidden="true"><UdyamMitraLogo variant={inverse ? "transparent" : "light"} decorative /></span><span><strong>{preserveName ? "UdyamMitra" : <LocalizedText value={"UdyamMitra"} />}</strong><small><LocalizedText value={"Rural Business Advisory Platform"} /></small><em>ग्रामीण उद्यम मार्गदर्शन</em></span></Link> }
