import { Sprout } from 'lucide-react'
import { Link } from 'react-router-dom'
import { cn } from '../../utils/cn'
export function Brand({ inverse = false }: { inverse?: boolean }) { return <Link to="/" className={cn('brand', inverse && 'brand--inverse')} aria-label="UdyamMitra home"><span className="brand__mark" aria-hidden="true"><Sprout size={25} /></span><span><strong>UdyamMitra</strong><small>Rural Business Advisory Platform</small><em>ग्रामीण उद्यम मार्गदर्शन</em></span></Link> }
