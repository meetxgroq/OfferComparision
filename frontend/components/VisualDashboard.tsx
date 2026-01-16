'use client'

import { motion } from 'framer-motion'
import {
    TrophyIcon,
    ShieldCheckIcon,
    RocketLaunchIcon,
    ExclamationTriangleIcon,
    CheckCircleIcon,
    XCircleIcon
} from '@heroicons/react/24/solid'
import { Radar } from 'react-chartjs-2'

interface VisualDashboardProps {
    analysis: any // JSON object from AI
    offer: any
}

export default function VisualDashboard({ analysis, offer }: VisualDashboardProps) {
    // Safe parsing if analysis is string (fallback)
    let data = analysis
    if (typeof analysis === 'string') {
        try {
            data = JSON.parse(analysis)
        } catch (e) {
            return <div className="text-slate-400 italic">Visual analysis unavailable for this offer.</div>
        }
    }

    const { verdict, scores, key_insights } = data || {}

    if (!verdict) return null

    // Badge Logic
    const getBadgeIcon = (badge: string) => {
        if (badge.includes('Top')) return TrophyIcon
        if (badge.includes('Safe')) return ShieldCheckIcon
        if (badge.includes('Growth')) return RocketLaunchIcon
        return TrophyIcon
    }

    const BadgeIcon = getBadgeIcon(verdict.badge || '')

    // Radar Data for this specific offer
    const radarData = {
        labels: ['Comp', 'WLB', 'Growth', 'Stability', 'Culture'],
        datasets: [{
            label: 'AI Score',
            data: [
                scores?.compensation || 0,
                scores?.work_life_balance || 0,
                scores?.growth_potential || 0,
                scores?.job_stability || 0,
                scores?.culture_fit || 0
            ],
            backgroundColor: 'rgba(6, 182, 212, 0.2)', // cyan-500
            borderColor: '#06b6d4',
            pointBackgroundColor: '#06b6d4',
            borderWidth: 2,
        }]
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-slate-800/50 rounded-xl border border-slate-700 overflow-hidden mb-6"
        >
            {/* 1. Verdict Header */}
            <div className={`p-6 border-b border-slate-700 flex items-center justify-between bg-gradient-to-r from-slate-800 to-slate-900`}>
                <div>
                    <h3 className="text-xl font-bold text-white flex items-center space-x-3">
                        <span>{offer.company}</span>
                        <span className={`px-3 py-1 rounded-full text-xs font-bold bg-cyan-900/50 text-cyan-300 border border-cyan-700/50 flex items-center space-x-1`}>
                            <BadgeIcon className="h-3 w-3" />
                            <span>{verdict.badge}</span>
                        </span>
                    </h3>
                    <p className="text-slate-400 text-sm mt-1">"{verdict.one_line_summary}"</p>
                </div>
                <div className="text-right hidden sm:block">
                    <div className="text-2xl font-bold text-white">{scores?.growth_potential}/10</div>
                    <div className="text-xs text-slate-500 uppercase tracking-wider">Growth Score</div>
                </div>
            </div>

            {/* 2. Visual Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-0 divide-y md:divide-y-0 md:divide-x divide-slate-700">

                {/* Col 1: Radar Chart */}
                <div className="p-6 flex flex-col items-center justify-center">
                    <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4">Fit Profile</h4>
                    <div className="h-40 w-full relative">
                        <Radar
                            data={radarData}
                            options={{
                                responsive: true,
                                maintainAspectRatio: false,
                                scales: {
                                    r: {
                                        min: 0, max: 10,
                                        ticks: { display: false },
                                        grid: { color: 'rgba(255,255,255,0.05)' },
                                        pointLabels: { color: '#94a3b8', font: { size: 10 } }
                                    }
                                },
                                plugins: { legend: { display: false } }
                            }}
                        />
                    </div>
                </div>

                {/* Col 2: Pros */}
                <div className="p-6 bg-slate-800/30">
                    <h4 className="text-xs font-bold text-emerald-500 uppercase tracking-wider mb-4 flex items-center">
                        <CheckCircleIcon className="h-4 w-4 mr-1" /> Key Strengths
                    </h4>
                    <ul className="space-y-3">
                        {key_insights?.pros?.slice(0, 3).map((pro: string, idx: number) => (
                            <li key={idx} className="text-sm text-slate-300 flex items-start">
                                <span className="mr-2 text-emerald-500/50">•</span>
                                {pro}
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Col 3: Cons */}
                <div className="p-6 bg-slate-800/30">
                    <h4 className="text-xs font-bold text-rose-500 uppercase tracking-wider mb-4 flex items-center">
                        <XCircleIcon className="h-4 w-4 mr-1" /> Risks & Gaps
                    </h4>
                    <ul className="space-y-3">
                        {key_insights?.cons?.slice(0, 3).map((con: string, idx: number) => (
                            <li key={idx} className="text-sm text-slate-300 flex items-start">
                                <span className="mr-2 text-rose-500/50">•</span>
                                {con}
                            </li>
                        ))}
                    </ul>
                </div>

            </div>
        </motion.div>
    )
}
