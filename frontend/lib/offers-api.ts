import axios from 'axios'
import { getApiBase, authHeaders } from '@/lib/api'
import type { Offer } from '@/types'

export interface SavedOffer {
  id: string
  client_id: string | null
  company: string
  position: string
  location: string
  base_salary: number
  equity: number
  bonus: number
  signing_bonus?: number
  total_compensation?: number
  years_experience?: number
  vesting_years?: number
  level?: string
  benefits_grade?: string
  wlb_grade?: string
  growth_grade?: string
  wlb_score?: number
  growth_score?: number
  work_type?: string
  employment_type?: string
  domain?: string
  job_description?: string
  other_perks?: string
  relocation_support?: boolean
  currency?: string
  country?: string
  created_at?: string
  updated_at?: string
}

export async function fetchSavedOffers(token: string): Promise<SavedOffer[]> {
  const res = await axios.get(`${getApiBase()}/api/offers`, {
    headers: authHeaders(token),
  })
  return res.data
}

export async function saveOffersToCloud(
  token: string,
  offers: Offer[]
): Promise<SavedOffer[]> {
  const res = await axios.post(
    `${getApiBase()}/api/offers`,
    { offers },
    { headers: authHeaders(token) }
  )
  return res.data
}

export async function deleteOfferFromCloud(
  token: string,
  clientId: string
): Promise<void> {
  await axios.delete(`${getApiBase()}/api/offers/${clientId}?by=client_id`, {
    headers: authHeaders(token),
  })
}
