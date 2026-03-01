/**
 * API base URL for backend. Set via NEXT_PUBLIC_API_BASE (e.g. in Vercel).
 */
export function getApiBase(): string {
  if (typeof window !== 'undefined') {
    return (process.env.NEXT_PUBLIC_API_BASE || '').replace(/\/$/, '') || 'http://localhost:8001'
  }
  return process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'
}

/**
 * Headers for authenticated API calls. Pass the Supabase access token.
 */
export function authHeaders(accessToken: string | null): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`
  }
  return headers
}
