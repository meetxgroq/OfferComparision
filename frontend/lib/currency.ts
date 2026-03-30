const CURRENCY_SYMBOLS: Record<string, string> = {
  USD: "$", INR: "₹", AED: "د.إ", GBP: "£", EUR: "€",
  SGD: "S$", CAD: "C$", AUD: "A$", JPY: "¥", CHF: "CHF",
  SEK: "kr", NOK: "kr", DKK: "kr", PLN: "zł", CZK: "Kč",
  ILS: "₪", KRW: "₩", TWD: "NT$", CNY: "¥", BRL: "R$",
  MXN: "$", SAR: "﷼", QAR: "﷼", THB: "฿", VND: "₫",
  IDR: "Rp", MYR: "RM", PHP: "₱", NZD: "NZ$", HKD: "HK$",
}

const CURRENCY_LOCALES: Record<string, string> = {
  USD: "en-US", INR: "en-IN", AED: "ar-AE", GBP: "en-GB", EUR: "de-DE",
  SGD: "en-SG", CAD: "en-CA", AUD: "en-AU", JPY: "ja-JP", CHF: "de-CH",
  KRW: "ko-KR", BRL: "pt-BR", MXN: "es-MX",
}

// 1 unit → USD (mirrors backend utils/currency.py, approximate mid-market early 2026)
const FX_RATES_TO_USD: Record<string, number> = {
  USD: 1.0,
  INR: 0.0119, AED: 0.272, GBP: 1.27, EUR: 1.08, SGD: 0.74,
  CAD: 0.71, AUD: 0.65, JPY: 0.00665, CHF: 1.12, SEK: 0.095,
  NOK: 0.091, DKK: 0.145, PLN: 0.25, CZK: 0.043, ILS: 0.27,
  KRW: 0.00068, TWD: 0.031, CNY: 0.138, BRL: 0.18, MXN: 0.055,
  SAR: 0.267, QAR: 0.275, THB: 0.028, VND: 0.000038, IDR: 0.000062,
  MYR: 0.22, PHP: 0.017, NZD: 0.59, HKD: 0.128,
}

export function convertCurrency(amount: number, from: string, to: string): number {
  if (from === to) return amount
  const fromRate = FX_RATES_TO_USD[from]
  const toRate = FX_RATES_TO_USD[to]
  if (!fromRate || !toRate) return amount
  return (amount * fromRate) / toRate
}

export function getCurrencySymbol(currency: string): string {
  return CURRENCY_SYMBOLS[currency] || currency
}

export function formatCurrency(amount: number, currency: string): string {
  const locale = CURRENCY_LOCALES[currency] || "en-US"
  try {
    return new Intl.NumberFormat(locale, {
      style: "currency",
      currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  } catch {
    const symbol = getCurrencySymbol(currency)
    return `${symbol}${amount.toLocaleString()}`
  }
}

export function formatCurrencyPair(
  localAmount: number,
  localCurrency: string,
  normalizedAmount: number,
  comparisonCurrency: string
): string {
  if (localCurrency === comparisonCurrency) {
    return formatCurrency(localAmount, localCurrency)
  }
  const local = formatCurrency(localAmount, localCurrency)
  const normalized = formatCurrency(normalizedAmount, comparisonCurrency)
  return `${local} (≈ ${normalized})`
}
