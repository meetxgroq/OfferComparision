export interface Offer {
  id: string
  company: string
  position: string
  location: string
  base_salary: number
  equity: number
  bonus: number
  signing_bonus?: number
  work_type: 'hybrid' | 'remote' | 'onsite'
  employment_type: 'full-time' | 'part-time' | 'freelance'
  domain?: string
  level?: string
  benefits_grade?: string
  wlb_grade?: string
  wlb_score?: number
  growth_grade?: string
  growth_score?: number
  // role_fit removed
  job_description?: string
  relocation_support?: boolean
  other_perks?: string
  total_compensation?: number

  // Analysis results (populated after API call)
  col_adjusted_salary?: number
  market_percentile?: number
  total_score?: number
  ai_analysis?: string
  company_research?: any
  market_sentiment?: any
}

export interface UserPreferences {
  salary_weight: number
  equity_weight: number
  wlb_weight: number
  growth_weight: number
  culture_weight: number
  benefits_weight: number
}

export interface UserProfile {
  name?: string
  email?: string
  resume_text?: string
  skills?: string[]
  experience_years?: number
  current_location?: string
  preferred_locations?: string[]
}

export interface AnalysisResults {
  executive_summary: string
  final_report: {
    report_type?: string
    detailed_analysis: string
    decision_framework: string
    offer_rankings: Array<{
      offer_id: string
      company: string
      position: string
      total_score: number
      rank: number
      ai_recommendation?: string
    }>
    verdict?: {
      recommended_company: string | null
      is_tie?: boolean
      summary_reasoning?: string
      financial_superiority?: boolean
      reasoning?: string[]
      career_growth_considerations?: string
    }
    net_value_analysis?: {
      offers: Array<{
        offer_id: string
        company: string
        gross_total: number
        estimated_tax: number
        net_take_home: number
        annual_col: number
        final_discretionary_income: number
      }>
      winner: string
    }
    negotiation_options?: Array<{
      id: string
      company?: string
      title: string
      difficulty: string
      description: string
      script: string
      difficulty_label?: string
      financial_impact?: string
    }>
    negotiation_opportunities?: string[]
    lifestyle_comparison?: {
      location_tradeoffs?: string
      hidden_costs?: string
    }
  }
  comparison_results: {
    ranked_offers: Array<{
      offer_id: string
      company: string
      position: string
      location: string
      total_score: number
      rating: string
      score_breakdown: any
      offer_data: any
      rank: number
      score_gap?: number
      market_percentile?: number
      market_median?: number
      ai_recommendation?: any
    }>
    top_offer?: any
    comparison_summary: string
    weights_used: any
  }
  visualization_data: {
    chart_data?: any
    comparison_table?: any
    radar_chart?: any
  }
  offers?: Array<any>
}

export interface FileUploadProps {
  onFileUpload: (file: File) => void
  acceptedTypes: string[]
  maxSize: number
  placeholder: string
}

export const WORK_TYPES = [
  { value: 'hybrid', label: 'Hybrid' },
  { value: 'remote', label: 'Remote' },
  { value: 'onsite', label: 'On-site' }
] as const

export const EMPLOYMENT_TYPES = [
  { value: 'full-time', label: 'Full-time' },
  { value: 'part-time', label: 'Part-time' },
  { value: 'freelance', label: 'Freelance' }
] as const

export const DOMAINS = [
  { value: 'backend', label: 'Backend Engineering' },
  { value: 'frontend', label: 'Frontend Development' },
  { value: 'fullstack', label: 'Full Stack Development' },
  { value: 'ai-ml', label: 'AI/ML' },
  { value: 'data-science', label: 'Data Science' },
  { value: 'cloud', label: 'Cloud Infrastructure' },
  { value: 'devops', label: 'DevOps' },
  { value: 'mobile', label: 'Mobile Development' },
  { value: 'security', label: 'Cybersecurity' },
  { value: 'fintech', label: 'Fintech' },
  { value: 'product', label: 'Product Management' },
  { value: 'design', label: 'Design' },
  { value: 'qa', label: 'QA Engineering' }
] as const

export const BENEFITS_GRADES = [
  {
    value: 'A+',
    label: 'A+ (Exceptional)',
    description: 'Premium health, unlimited PTO, stock program'
  },
  {
    value: 'A',
    label: 'A (Excellent)',
    description: 'Great health, generous PTO, good perks'
  },
  {
    value: 'B+',
    label: 'B+ (Good)',
    description: 'Standard health, reasonable PTO, some perks'
  },
  {
    value: 'B',
    label: 'B (Average)',
    description: 'Basic health, standard PTO, minimal perks'
  },
  {
    value: 'C+',
    label: 'C+ (Below Average)',
    description: 'Limited health, restricted PTO'
  },
  {
    value: 'C',
    label: 'C (Poor)',
    description: 'Minimal benefits, no additional perks'
  }
] as const
