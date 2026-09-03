import { z } from 'zod'
import { capitalRanges } from '../../types/analysis'

const text = (label: string) =>
  z
    .string()
    .trim()
    .min(2, `${label} is required.`)

const money = z
  .string()
  .trim()
  .min(1, 'Enter an amount.')
  .refine(
    value => Number.isFinite(Number(value)) && Number(value) >= 0,
    'Enter a valid non-negative amount.'
  )

const selectionItemSchema = z.object({
  name: z.string().min(1, 'Item name is required.'),
  otherDescription: z
    .string()
    .nullish()
    .transform(v => (v ? v.trim() : undefined)),
})

const selections = z
  .array(selectionItemSchema)
  .refine(
    items => !items.some(i => i.name === 'Other' && !i.otherDescription?.trim()),
    'Please describe your Other selection.'
  )

export const stepSchemas = [
  // Step 1: Personal Details
  z.object({
    fullName: text('Full name'),
    ageGroup: z.string().min(1, 'Select an age group.'),
    education: z.string().nullish(),
    previousExperience: z.string().min(1, 'Select your experience.'),
    preferredLanguage: z.string().min(1, 'Select your preferred language.'),
  }),

  // Step 2: Location
  z.object({
    state: text('State'),
    district: text('District'),
    taluka: text('Taluka'),
    village: text('Village'),
    pincode: z
      .string()
      .regex(/^[1-9]\d{5}$/, 'Enter a valid 6-digit pincode.'),
  }),

  // Step 3: Capital
  z.object({
    capitalRange: z.enum(capitalRanges, { error: 'Select a valid capital range.' }),
    ownCapital: money,
    loanRequired: money,
  }),

  // Step 4: Skills
  z.object({
    skills: selections,
  }),

  // Step 5: Resources
  z.object({
    resources: selections,
  }),

  // Step 6: Existing Business
  z.object({
    hasExistingBusiness: z.boolean({ error: 'Please specify if you currently run a business.' }),
    existingBusiness: z
      .object({
        businessName: z.string().nullish(),
        businessCategory: z.string().nullish(),
        yearsOperating: z.coerce.number().nullish(),
        initialInvestment: z.string().nullish(),
        monthlyRevenue: z.string().nullish(),
        monthlyExpenses: z.string().nullish(),
        employeeCount: z.coerce.number().nullish(),
        estimatedMonthlyCustomers: z.coerce.number().nullish(),
        majorChallenges: z.string().nullish(),
      })
      .nullish(),
  }).superRefine((value, ctx) => {
    if (!value.hasExistingBusiness) return
    const b = value.existingBusiness
    if (!b || !b.businessName || b.businessName.trim().length < 2) {
      ctx.addIssue({
        code: 'custom',
        message: 'Enter a valid business name (minimum 2 characters).',
        path: ['existingBusiness', 'businessName'],
      })
    }
    if (!b || !b.businessCategory || b.businessCategory.trim().length < 2) {
      ctx.addIssue({
        code: 'custom',
        message: 'Enter a business category (minimum 2 characters).',
        path: ['existingBusiness', 'businessCategory'],
      })
    }
    for (const key of ['initialInvestment', 'monthlyRevenue', 'monthlyExpenses'] as const) {
      const val = b ? b[key] : undefined
      if (val === undefined || val === null || val === '' || !Number.isFinite(Number(val)) || Number(val) < 0) {
        ctx.addIssue({
          code: 'custom',
          message: 'Enter valid non-negative business figures.',
          path: ['existingBusiness', key],
        })
      }
    }
  }),
]

export function formatValidationError(issue?: z.ZodIssue): string {
  if (!issue) return 'Please complete all required fields.'
  if (
    issue.message.startsWith('Invalid input:') ||
    issue.message.includes('expected string') ||
    issue.message.includes('received null') ||
    issue.message.includes('Expected')
  ) {
    const field = issue.path[issue.path.length - 1]
    if (typeof field === 'string') {
      return `Please enter a valid value for ${field.replace(/([A-Z])/g, ' $1').toLowerCase()}.`
    }
    return 'Please complete all required fields.'
  }
  return issue.message
}


