import { z } from 'zod'

export const identifierSchema = z.string().trim().min(1, 'Enter your email address or mobile number.').refine(value => /^\d+$/.test(value) ? /^[6-9]\d{9}$/.test(value) : z.string().email().safeParse(value).success, 'Enter a valid email address or Indian 10-digit mobile number.')
const passwordSchema = z.string().min(8, 'Password must contain at least 8 characters.').regex(/[A-Z]/, 'Add at least one uppercase letter.').regex(/[a-z]/, 'Add at least one lowercase letter.').regex(/\d/, 'Add at least one number.')

export const loginSchema = z.object({ identifier: identifierSchema, password: z.string().min(1, 'Enter your password.'), rememberMe: z.boolean() })
export const registerSchema = z.object({
  fullName: z.string().trim().min(2, 'Full name must contain at least 2 characters.'),
  mobile: z.string().trim().regex(/^[6-9]\d{9}$/, 'Enter a valid Indian 10-digit mobile number.'),
  email: z.string().trim().email('Enter a valid email address.'),
  preferredLanguage: z.enum(['en', 'mr', 'hi'], { error: 'Select your preferred language.' }),
  password: passwordSchema, confirmPassword: z.string().min(1, 'Confirm your password.'),
  termsAccepted: z.boolean().refine(value => value, 'You must accept the Terms of Use and Privacy Policy.'),
}).refine(data => data.password === data.confirmPassword, { path: ['confirmPassword'], message: 'Passwords do not match.' })
export const forgotPasswordSchema = z.object({ identifier: identifierSchema })

export type LoginFormData = z.infer<typeof loginSchema>
export type RegisterFormData = z.infer<typeof registerSchema>
export type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>
