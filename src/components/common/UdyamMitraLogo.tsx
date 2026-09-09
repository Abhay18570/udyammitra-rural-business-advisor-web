import { cn } from '../../utils/cn'

export const udyamMitraLogoPath = '/assets/branding/udyammitra-logo.jpeg'
export const udyamMitraTransparentLogoPath = '/assets/branding/udyammitra-logo-transparent.png'
const sizes = { small: 44, medium: 56, large: 78 } as const

/** The supplied artwork is displayed intact. Adjacent brand text supplies the name when decorative. */
export function UdyamMitraLogo({ variant = 'light', size = 'medium', decorative = false, className }: {
  variant?: 'light' | 'transparent'
  size?: keyof typeof sizes
  decorative?: boolean
  className?: string
}) {
  return <img src={variant === 'transparent' ? udyamMitraTransparentLogoPath : udyamMitraLogoPath} alt={decorative ? '' : 'UdyamMitra'} aria-hidden={decorative || undefined}
    width={sizes[size]} height={sizes[size]} loading="eager" decoding="async"
    className={cn('udyammitra-logo', `udyammitra-logo--${size}`, `udyammitra-logo--${variant}`, className)} />
}
