export type CurrencyOption = { code: string; symbol: string; name: string }

export const FALLBACK_CURRENCIES: CurrencyOption[] = [
  { code: 'USD', symbol: '$', name: 'US Dollar' },
  { code: 'INR', symbol: '₹', name: 'Indian Rupee' },
  { code: 'GBP', symbol: '£', name: 'British Pound' },
  { code: 'EUR', symbol: '€', name: 'Euro' },
  { code: 'AED', symbol: 'د.إ', name: 'UAE Dirham' },
  { code: 'SGD', symbol: 'S$', name: 'Singapore Dollar' },
  { code: 'CAD', symbol: 'C$', name: 'Canadian Dollar' },
  { code: 'AUD', symbol: 'A$', name: 'Australian Dollar' },
  { code: 'JPY', symbol: '¥', name: 'Japanese Yen' },
  { code: 'CHF', symbol: 'CHF', name: 'Swiss Franc' },
]

export function mergeCurrencies(apiData: unknown): CurrencyOption[] {
  const merged = new Map<string, CurrencyOption>(
    FALLBACK_CURRENCIES.map((c) => [c.code, c])
  )

  if (Array.isArray(apiData)) {
    for (const item of apiData) {
      if (
        item &&
        typeof item === 'object' &&
        'code' in item &&
        'symbol' in item &&
        'name' in item &&
        typeof (item as any).code === 'string' &&
        typeof (item as any).symbol === 'string' &&
        typeof (item as any).name === 'string'
      ) {
        const c = item as CurrencyOption
        merged.set(c.code, c)
      }
    }
  }

  return Array.from(merged.values()).sort((a, b) => a.code.localeCompare(b.code))
}
