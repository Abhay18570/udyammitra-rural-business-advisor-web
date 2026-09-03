const DECIMAL_AMOUNT = /^([+-]?)(\d+)(?:\.(\d{1,2}))?$/

/** Parse an API decimal string into integer paise without floating-point arithmetic. */
export function parseINRToPaise(value: string): bigint | null {
  const match = DECIMAL_AMOUNT.exec(value.trim())
  if (!match) return null
  const [, sign, rupees, fraction = ''] = match
  const paise = BigInt(rupees) * 100n + BigInt(fraction.padEnd(2, '0'))
  return sign === '-' ? -paise : paise
}

export function formatINR(value: string, options: { fractionDigits?: 0 | 2; fallback?: string } = {}): string {
  const paise = parseINRToPaise(value)
  if (paise === null) return options.fallback ?? 'Not available'
  const fractionDigits = options.fractionDigits ?? 0
  const negative = paise < 0n
  const absolute = negative ? -paise : paise
  // Whole-rupee displays use documented half-up rounding; stored/API values retain paise.
  const wholeRupees = fractionDigits === 0 ? (absolute + 50n) / 100n : absolute / 100n
  const formatted = new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(wholeRupees)
  const fraction = fractionDigits === 2 ? `.${String(absolute % 100n).padStart(2, '0')}` : ''
  return `${negative ? '-' : ''}₹${formatted}${fraction}`
}
