
export interface CompanyData {
    name: string
    benefits_grade: 'A+' | 'A' | 'B+' | 'B' | 'C+' | 'C'
    wlb_grade: 'A+' | 'A' | 'B+' | 'B' | 'C+' | 'C'
    growth_grade: 'A+' | 'A' | 'B+' | 'B' | 'C+' | 'C'
    levels?: string[]
}

export const POPULAR_COMPANIES: CompanyData[] = [
    // MAANG / Big Tech
    { name: 'Google', benefits_grade: 'A+', wlb_grade: 'B+', growth_grade: 'A+', levels: ['L3', 'L4', 'L5', 'L6', 'L7', 'L8'] },
    { name: 'Microsoft', benefits_grade: 'A', wlb_grade: 'A', growth_grade: 'A', levels: ['59', '60', '61', '62', '63', '64', '65', '66', '67', '64 / Senior Manager', 'Principal EM', 'Partner', 'VP'] },
    { name: 'Meta (Facebook)', benefits_grade: 'A+', wlb_grade: 'B', growth_grade: 'A+', levels: ['E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9'] },
    { name: 'Apple', benefits_grade: 'A', wlb_grade: 'B', growth_grade: 'A', levels: ['ICT2', 'ICT3', 'ICT4', 'ICT5', 'ICT6'] },
    { name: 'Amazon', benefits_grade: 'B+', wlb_grade: 'C+', growth_grade: 'A+', levels: ['L4', 'L5', 'L6', 'L7', 'L8'] },
    { name: 'Netflix', benefits_grade: 'A+', wlb_grade: 'C+', growth_grade: 'A+', levels: ['L4', 'L5', 'L6'] },

    // AI & Frontier Tech
    { name: 'OpenAI', benefits_grade: 'A+', wlb_grade: 'C+', growth_grade: 'A+', levels: ['L4', 'L5', 'L6'] },
    { name: 'Anthropic', benefits_grade: 'A', wlb_grade: 'B', growth_grade: 'A+', levels: ['L4', 'L5', 'L6'] },
    { name: 'Groq', benefits_grade: 'A', wlb_grade: 'B', growth_grade: 'A+', levels: ['L4', 'L5', 'L6'] },
    { name: 'Perplexity AI', benefits_grade: 'A', wlb_grade: 'B', growth_grade: 'A+', levels: ['L4', 'L5', 'L6'] },
    { name: 'Databricks', benefits_grade: 'A', wlb_grade: 'B', growth_grade: 'A+', levels: ['L3', 'L4', 'L5', 'L6'] },
    { name: 'Snowflake', benefits_grade: 'A', wlb_grade: 'C', growth_grade: 'A', levels: ['L3', 'L4', 'L5', 'L6'] },
    { name: 'Palantir', benefits_grade: 'A+', wlb_grade: 'C', growth_grade: 'A', levels: ['L3', 'L4', 'L5', 'L6'] },

    // Hardware / Chips
    { name: 'NVIDIA', benefits_grade: 'A+', wlb_grade: 'B', growth_grade: 'A+', levels: ['IC1', 'IC2', 'IC3', 'IC4', 'IC5', 'IC6', 'IC7', 'IC8'] },
    { name: 'AMD', benefits_grade: 'B+', wlb_grade: 'C+', growth_grade: 'B+', levels: ['P10', 'P20', 'P30', 'P40', 'P50'] },
    { name: 'Intel', benefits_grade: 'B+', wlb_grade: 'B', growth_grade: 'B', levels: ['Grade 5', 'Grade 6', 'Grade 7', 'Grade 8', 'Grade 9'] },
    { name: 'Qualcomm', benefits_grade: 'A', wlb_grade: 'B+', growth_grade: 'B+', levels: ['Associate', 'Senior', 'Staff', 'Senior Staff', 'Principal'] },
    { name: 'Broadcom', benefits_grade: 'A', wlb_grade: 'C+', growth_grade: 'B+', levels: ['IC1', 'IC2', 'IC3', 'IC4', 'IC5'] },
    { name: 'TSMC', benefits_grade: 'B', wlb_grade: 'C', growth_grade: 'A', levels: ['Grade 31', 'Grade 32', 'Grade 33', 'Grade 34'] },
    { name: 'Samsung', benefits_grade: 'B+', wlb_grade: 'C+', growth_grade: 'B', levels: ['L1', 'L2', 'L3', 'L4'] },

    // Social Media & Consumer
    { name: 'Instagram', benefits_grade: 'A+', wlb_grade: 'C+', growth_grade: 'A+', levels: ['L3', 'L4', 'L5', 'L6', 'L7'] },
    { name: 'YouTube', benefits_grade: 'A+', wlb_grade: 'A', growth_grade: 'A', levels: ['L3', 'L4', 'L5', 'L6', 'L7'] },
    { name: 'TikTok (ByteDance)', benefits_grade: 'A', wlb_grade: 'C', growth_grade: 'A+', levels: ['1-1', '1-2', '2-1', '2-2', '3-1', '3-2'] },
    { name: 'X (Twitter)', benefits_grade: 'B', wlb_grade: 'C', growth_grade: 'A', levels: ['L3', 'L4', 'L5', 'L6'] },
    { name: 'LinkedIn', benefits_grade: 'A+', wlb_grade: 'A', growth_grade: 'A', levels: ['Associate', 'Senior', 'Staff', 'Senior Staff', 'Principal'] },
    { name: 'Pinterest', benefits_grade: 'A+', wlb_grade: 'A', growth_grade: 'B+', levels: ['L3', 'L4', 'L5', 'L6'] },
    { name: 'Snap Inc.', benefits_grade: 'A', wlb_grade: 'C+', growth_grade: 'B+', levels: ['L3', 'L4', 'L5', 'L6'] },
    { name: 'Reddit', benefits_grade: 'A', wlb_grade: 'A', growth_grade: 'B+', levels: ['L3', 'L4', 'L5', 'L6'] },
    { name: 'Spotify', benefits_grade: 'A', wlb_grade: 'A', growth_grade: 'B+', levels: ['L1', 'L2', 'L3', 'L4'] },

    // Autonomous / Auto
    { name: 'Tesla', benefits_grade: 'B+', wlb_grade: 'C', growth_grade: 'A+', levels: ['P1', 'P2', 'P3', 'P4'] },
    { name: 'SpaceX', benefits_grade: 'B+', wlb_grade: 'C', growth_grade: 'A+', levels: ['L1', 'L2', 'L3', 'L4'] },
    { name: 'Waymo', benefits_grade: 'A+', wlb_grade: 'B', growth_grade: 'A+', levels: ['L3', 'L4', 'L5', 'L6'] },
    { name: 'Zoox', benefits_grade: 'B+', wlb_grade: 'C+', growth_grade: 'A+', levels: ['L3', 'L4', 'L5'] },
    { name: 'Cruise', benefits_grade: 'A', wlb_grade: 'C+', growth_grade: 'A', levels: ['L3', 'L4', 'L5', 'L6'] },
    { name: 'Rivian', benefits_grade: 'B+', wlb_grade: 'C+', growth_grade: 'A', levels: ['L3', 'L4', 'L5'] },

    // Enterprise / SaaS
    { name: 'Salesforce', benefits_grade: 'A', wlb_grade: 'A', growth_grade: 'A', levels: ['AMTS', 'MTS', 'SMTS', 'LMTS', 'Principal'] },
    { name: 'Adobe', benefits_grade: 'A', wlb_grade: 'A', growth_grade: 'A', levels: ['L3', 'L4', 'L5', 'L6'] },
    { name: 'Oracle', benefits_grade: 'B+', wlb_grade: 'B', growth_grade: 'B+', levels: ['IC1', 'IC2', 'IC3', 'IC4', 'IC5'] },
    { name: 'Cisco', benefits_grade: 'A', wlb_grade: 'A', growth_grade: 'B+', levels: ['Grade 4', 'Grade 6', 'Grade 8', 'Grade 10'] },
    { name: 'IBM', benefits_grade: 'B+', wlb_grade: 'B+', growth_grade: 'B', levels: ['Band 6', 'Band 7', 'Band 8', 'Band 9', 'Band 10'] },
    { name: 'Intuit', benefits_grade: 'A', wlb_grade: 'A', growth_grade: 'A', levels: ['L2', 'L3', 'L4', 'L5'] },
    { name: 'Workday', benefits_grade: 'A', wlb_grade: 'A', growth_grade: 'B+', levels: ['P1', 'P2', 'P3', 'P4'] },
    { name: 'ServiceNow', benefits_grade: 'A', wlb_grade: 'B+', growth_grade: 'A', levels: ['IC1', 'IC2', 'IC3', 'IC4', 'IC5'] },
    { name: 'Atlassian', benefits_grade: 'A+', wlb_grade: 'A', growth_grade: 'A', levels: ['P3', 'P4', 'P5', 'P6'] },
    { name: 'Zoom', benefits_grade: 'A', wlb_grade: 'A', growth_grade: 'B', levels: ['L2', 'L3', 'L4', 'L5'] },
    { name: 'HubSpot', benefits_grade: 'A', wlb_grade: 'A', growth_grade: 'A', levels: ['Entry', 'Senior', 'Staff', 'Principal'] },
    { name: 'Shopify', benefits_grade: 'A', wlb_grade: 'A', growth_grade: 'A', levels: ['L5', 'L6', 'L7', 'L8'] },

    // Fintech
    { name: 'Stripe', benefits_grade: 'A+', wlb_grade: 'B', growth_grade: 'A+', levels: ['L1', 'L2', 'L3', 'L4'] },
    { name: 'Coinbase', benefits_grade: 'A', wlb_grade: 'C', growth_grade: 'A+', levels: ['IC3', 'IC4', 'IC5', 'IC6'] },
    { name: 'Robinhood', benefits_grade: 'A', wlb_grade: 'C+', growth_grade: 'A', levels: ['L1', 'L2', 'L3', 'L4'] },
    { name: 'Block (Square)', benefits_grade: 'A', wlb_grade: 'C+', growth_grade: 'A', levels: ['L3', 'L4', 'L5', 'L6'] },
    { name: 'PayPal', benefits_grade: 'B+', wlb_grade: 'B', growth_grade: 'B+', levels: ['IC1', 'IC2', 'IC3', 'IC4', 'IC5'] },
    { name: 'SoFi', benefits_grade: 'A', wlb_grade: 'B', growth_grade: 'A', levels: ['L1', 'L2', 'L3', 'L4', 'L5'] },

    // Gig / Travel
    { name: 'Uber', benefits_grade: 'A', wlb_grade: 'B', growth_grade: 'A', levels: ['L3', 'L4', 'L5', 'L6'] },
    { name: 'Lyft', benefits_grade: 'A', wlb_grade: 'B', growth_grade: 'B+', levels: ['T3', 'T4', 'T5', 'T6'] },
    { name: 'Airbnb', benefits_grade: 'A', wlb_grade: 'A', growth_grade: 'B+', levels: ['L3', 'L4', 'L5', 'L6'] },
    { name: 'DoorDash', benefits_grade: 'A', wlb_grade: 'C+', growth_grade: 'A', levels: ['E3', 'E4', 'E5', 'E6'] },

    // Gaming / Metaverse
    { name: 'Roblox', benefits_grade: 'A', wlb_grade: 'C', growth_grade: 'A', levels: ['IC1', 'IC2', 'IC3', 'IC4', 'IC5'] },
    { name: 'Unity', benefits_grade: 'A', wlb_grade: 'B', growth_grade: 'B+', levels: ['IC1', 'IC2', 'IC3', 'IC4', 'IC5'] },
    { name: 'Electronic Arts', benefits_grade: 'B+', wlb_grade: 'B', growth_grade: 'B', levels: ['L1', 'L2', 'L3', 'L4', 'L5'] },
    { name: 'Riot Games', benefits_grade: 'A+', wlb_grade: 'C+', growth_grade: 'A', levels: ['L1', 'L2', 'L3', 'L4', 'L5'] }
]
