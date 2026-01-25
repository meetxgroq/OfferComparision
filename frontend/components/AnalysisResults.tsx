'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  SparklesIcon,
  ChartBarIcon,
  TableCellsIcon,
  ClockIcon,
  DocumentArrowDownIcon,
  ChevronDownIcon,
  TrophyIcon,
  CurrencyDollarIcon,
  ScaleIcon,
  MapPinIcon,
  UserGroupIcon,
  LightBulbIcon,
  PresentationChartLineIcon,
  FireIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline'
import {
  TrophyIcon as TrophyIconSolid,
  CheckCircleIcon as CheckCircleIconSolid,
  ExclamationTriangleIcon as ExclamationTriangleIconSolid
} from '@heroicons/react/24/solid'
import { Radar, Bar, Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  RadialLinearScale,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js'
import ReactMarkdown from 'react-markdown'
import type { AnalysisResults } from '@/types'
import VisualDashboard from './VisualDashboard'

// Register Chart.js components
ChartJS.register(
  RadialLinearScale,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend
)

interface AnalysisResultsProps {
  results: AnalysisResults
}

export default function AnalysisResults({ results }: AnalysisResultsProps) {
  const [activeTab, setActiveTab] = useState<'ai' | 'charts' | 'table' | 'timeline'>('ai')
  const [selectedNegotiationOption, setSelectedNegotiationOption] = useState<string | null>(null)
  const [selectedNegotiationCompany, setSelectedNegotiationCompany] = useState<string | null>(null)
  const [showDetailed, setShowDetailed] = useState(false)
  const [copiedScriptId, setCopiedScriptId] = useState<string | null>(null)

  // Helper to format content for ReactMarkdown defensively
  const formatMarkdownContent = (content: any): string => {
    if (!content) return ''
    if (typeof content === 'string') return content

    if (Array.isArray(content)) {
      return content.map(item => {
        if (typeof item === 'object') return formatMarkdownContent(item)
        return `- ${item}`
      }).join('\n')
    }

    if (typeof content === 'object') {
      try {
        // Handle common keys
        if (content.points && Array.isArray(content.points)) return formatMarkdownContent(content.points)
        if (content.items && Array.isArray(content.items)) return formatMarkdownContent(content.items)

        // Convert object to nested bullet points
        return Object.entries(content).map(([key, value]) => {
          if (Array.isArray(value)) {
            return `- **${key}**\n${value.map(v => `  - ${v}`).join('\n')}`
          }
          if (typeof value === 'object') {
            return `- **${key}**\n${formatMarkdownContent(value).split('\n').map(l => `  ${l}`).join('\n')}`
          }
          return `- **${key}**: ${value}`
        }).join('\n')
      } catch (e) {
        return String(content)
      }
    }
    return String(content)
  }

  const tabs = [
    { id: 'ai', label: 'AI Recommendations', icon: SparklesIcon },
    { id: 'charts', label: 'Multi-Dimensional Analysis', icon: ChartBarIcon },
    { id: 'table', label: 'Detailed Comparison', icon: TableCellsIcon },
    { id: 'timeline', label: 'Decision Timeline', icon: ClockIcon }
  ]

  // Process data for charts
  const rankedOffers = results.comparison_results?.ranked_offers || []

  // stack bar data
  const barData = {
    labels: rankedOffers.map(o => o.company),
    datasets: [
      {
        label: 'Base Salary',
        data: rankedOffers.map(o => o.offer_data?.base_salary || 0),
        backgroundColor: '#06b6d4', // cyan-500
        stack: 'Stack 0',
      },
      {
        label: 'Equity',
        data: rankedOffers.map(o => o.offer_data?.equity || 0),
        backgroundColor: '#fcd34d', // amber-300
        stack: 'Stack 0',
      },
      {
        label: 'Bonus',
        data: rankedOffers.map(o => o.offer_data?.bonus || 0),
        backgroundColor: '#ef4444', // red-500
        stack: 'Stack 0',
      },
    ]
  }

  // radar data
  const radarData = {
    labels: ['Salary', 'Equity', 'Bonus', 'Benefits', 'Work-Life', 'Growth', 'Overall'],
    datasets: rankedOffers.map((offer, index) => ({
      label: offer.company,
      data: [
        // Normalize to 0-10 scale approximately
        Math.min(10, (offer.offer_data?.base_salary || 0) / 25000),
        Math.min(10, (offer.offer_data?.equity || 0) / 10000),
        Math.min(10, (offer.offer_data?.bonus || 0) / 5000),
        offer.offer_data?.benefits_grade === 'A+' ? 10 : offer.offer_data?.benefits_grade === 'A' ? 9 : 7,
        offer.offer_data?.wlb_score || 0,
        offer.offer_data?.growth_score || 0,
        offer.total_score ? offer.total_score / 10 : 5 // Fallback
      ],
      backgroundColor: index === 0 ? 'rgba(6, 182, 212, 0.2)' : 'rgba(251, 146, 60, 0.2)',
      borderColor: index === 0 ? '#06b6d4' : '#fb923c',
      pointBackgroundColor: index === 0 ? '#06b6d4' : '#fb923c',
      borderWidth: 2,
    }))
  }

  const exportToJSON = () => {
    const dataStr = JSON.stringify(results, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr)
    const exportFileDefaultName = 'offer-comparison-results.json'

    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-slate-900 rounded-2xl shadow-xl border border-slate-800 overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-slate-800 bg-slate-900/50">
        <h3 className="text-2xl font-bold text-white">Comprehensive Offer Analysis</h3>
        <button
          onClick={exportToJSON}
          className="flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-lg transition-colors border border-slate-700"
        >
          <DocumentArrowDownIcon className="h-4 w-4" />
          <span>Export Results</span>
        </button>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-slate-800 overflow-x-auto bg-slate-950/30">
        {tabs.filter(t => t.id !== 'table').map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center space-x-2 px-6 py-4 text-sm font-medium transition-colors whitespace-nowrap ${activeTab === tab.id
              ? 'text-cyan-400 border-b-2 border-cyan-400 bg-cyan-950/20'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
          >
            <tab.icon className="h-4 w-4" />
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="p-6 bg-slate-900 min-h-[600px]">
        {activeTab === 'ai' && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-8 max-w-5xl mx-auto"
          >
            {/* Executive Summary Section - Only for Full Analysis */}
            {results.executive_summary && results.final_report?.report_type === 'BenchMarked Analysis' && (
              <div className="bg-slate-800/20 p-8 rounded-3xl border border-white/5 shadow-2xl backdrop-blur-sm relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-4 opacity-10">
                  <LightBulbIcon className="h-24 w-24 text-amber-400 -rotate-12" />
                </div>

                <div className="flex items-center space-x-3 mb-6 relative z-10">
                  <div className="bg-amber-500/20 p-2.5 rounded-xl border border-amber-500/40">
                    <SparklesIcon className="h-6 w-6 text-amber-400" />
                  </div>
                  <div>
                    <h4 className="text-2xl font-black text-white tracking-tight">Executive Summary</h4>
                    <p className="text-slate-500 text-sm font-medium tracking-wide">High-level strategic overview</p>
                  </div>
                </div>

                <div className="relative z-10 prose prose-invert prose-lg max-w-none text-slate-300">
                  <div className="bg-slate-950/40 p-6 rounded-2xl border border-white/5 font-medium leading-relaxed whitespace-pre-wrap">
                    {results.executive_summary}
                  </div>
                </div>
              </div>
            )}
            {/* Smart Choice Verdict Section */}
            {results.final_report?.verdict && (
              <div className="relative mb-12 py-12 px-6 overflow-hidden">
                {/* Background decorative elements */}
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full opacity-10 pointer-events-none">
                  <div className="absolute top-0 left-1/4 w-64 h-64 bg-amber-500 rounded-full blur-[100px]" />
                  <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-sky-500 rounded-full blur-[100px]" />
                </div>

                <div className="relative z-10 flex flex-col items-center justify-center text-center">
                  <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-black capitalize tracking-widest mb-4 animate-pulse">
                    <SparklesIcon className="h-4 w-4" />
                    <span>Smart choice</span>
                  </div>

                  <div className="flex items-center justify-center space-x-6 mb-2">
                    <TrophyIconSolid className="h-10 w-10 text-amber-400 filter drop-shadow-[0_0_12px_rgba(251,191,36,0.4)] animate-bounce" />
                    <h2 className="text-5xl md:text-6xl font-extrabold text-white tracking-tight drop-shadow-xl">
                      {results.final_report.verdict.recommended_company}
                    </h2>
                    <TrophyIconSolid className="h-10 w-10 text-amber-400 filter drop-shadow-[0_0_12px_rgba(251,191,36,0.4)] animate-bounce" />
                  </div>

                  <div className="mb-4">
                    <p className="text-slate-400 text-lg font-medium italic opacity-80 max-w-2xl mx-auto leading-relaxed">
                      {results.final_report.verdict.is_tie ? "It's a tie!" : results.final_report.verdict.summary_reasoning}
                    </p>
                  </div>

                </div>
              </div>
            )}

            {/* Analysis Snapshot Section */}
            {rankedOffers.length > 0 && (
              <div className="bg-slate-800/20 p-8 pt-6 rounded-3xl border border-slate-700/30 overflow-hidden shadow-2xl backdrop-blur-sm -mt-12">
                <div className="flex items-center space-x-3 mb-8">
                  <div className="bg-sky-500/20 p-2.5 rounded-xl border border-sky-500/40">
                    <ChartBarIcon className="h-6 w-6 text-sky-400" />
                  </div>
                  <div>
                    <h4 className="text-2xl font-black text-white tracking-tight">Analysis Snapshot</h4>
                    <p className="text-slate-500 text-sm font-medium tracking-wide">High-level KPI comparison</p>
                  </div>
                </div>

                {/* Top Section: Mixed Bars and Cards */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
                  {/* Left: Financial Bars (Total Comp & Net Savings) */}
                  <div className="space-y-8 bg-slate-900/40 p-6 rounded-2xl border border-white/5">
                    {/* Total Compensation Bars */}
                    <div className="space-y-4">
                      <h5 className="text-xs font-black text-slate-400 tracking-widest pl-1">Total Compensation</h5>
                      <div className="space-y-3">
                        {(() => {
                          const maxVal = Math.max(...rankedOffers.map(o => o.offer_data?.total_compensation || 0), 1);
                          return rankedOffers.map((offer, idx) => {
                            const val = offer.offer_data?.total_compensation || 0;
                            const perc = (val / maxVal) * 100;
                            const isWinner = val === maxVal && val > 0;
                            return (
                              <div key={offer.offer_id} className="space-y-1.5">
                                <div className="flex justify-between items-end px-1">
                                  <span className="text-sm font-bold text-white uppercase tracking-tighter">{offer.company}</span>
                                  <span className="text-sm font-black text-white">${val.toLocaleString()}</span>
                                </div>
                                <div className="h-3 w-full bg-slate-800 rounded-full overflow-hidden border border-white/5 shadow-inner">
                                  <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${Math.max(perc, 5)}%` }}
                                    transition={{ duration: 1, ease: "easeOut" }}
                                    className={`h-full rounded-full ${isWinner ? 'bg-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.3)]' : 'bg-orange-500 shadow-[0_0_15px_rgba(249,115,22,0.2)]'}`}
                                  />
                                </div>
                              </div>
                            );
                          });
                        })()}
                      </div>
                    </div>

                    {/* Projected Net Savings Bars */}
                    <div className="space-y-4 pt-2">
                      <h5 className="text-xs font-black text-slate-400 tracking-widest pl-1">Projected Net Savings</h5>
                      <div className="space-y-3">
                        {(() => {
                          const maxVal = Math.max(...rankedOffers.map(o => o.offer_data?.net_savings || 0), 1);
                          return rankedOffers.map((offer, idx) => {
                            const val = offer.offer_data?.net_savings || 0;
                            const perc = (val / maxVal) * 100;
                            const isWinner = val === maxVal && val > 0;
                            return (
                              <div key={offer.offer_id} className="space-y-1.5">
                                <div className="flex justify-between items-end px-1">
                                  <span className="text-sm font-bold text-white uppercase tracking-tighter">{offer.company}</span>
                                  <span className="text-sm font-black text-cyan-400">${val.toLocaleString()}<span className="text-[10px] text-slate-500 ml-1">/yr</span></span>
                                </div>
                                <div className="h-3 w-full bg-slate-800 rounded-full overflow-hidden border border-white/5 shadow-inner">
                                  <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${Math.max(perc, 5)}%` }}
                                    transition={{ duration: 1, delay: 0.2, ease: "easeOut" }}
                                    className={`h-full rounded-full ${isWinner ? 'bg-emerald-400' : 'bg-orange-400 opacity-80'}`}
                                  />
                                </div>
                              </div>
                            );
                          });
                        })()}
                      </div>
                    </div>
                  </div>

                  <div className="space-y-6">
                    {/* Score Grid: Category Rows with Company Headers */}
                    <div className="bg-slate-900/40 p-5 rounded-2xl border border-white/5 h-full flex flex-col justify-center">
                      <div className="grid grid-cols-[100px_1fr_1fr] gap-4 mb-4">
                        <div /> {/* Empty corner */}
                        {rankedOffers.map(o => (
                          <div key={o.offer_id} className="text-[10px] font-black text-slate-400 uppercase tracking-widest text-center truncate px-2">
                            {o.company}
                          </div>
                        ))}
                      </div>

                      <div className="space-y-5">
                        {/* WLB Row */}
                        <div className="grid grid-cols-[100px_1fr_1fr] gap-4 items-center">
                          <div className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">WLB</div>
                          {rankedOffers.map(o => {
                            const grades = ['A+', 'A', 'B+', 'B', 'C+', 'C'];
                            const winnerGrade = grades.find(g => rankedOffers.some(ro => ro.offer_data?.wlb_grade === g));
                            const isWinner = o.offer_data?.wlb_grade === winnerGrade;
                            return (
                              <div key={o.offer_id} className={`py-2 rounded-xl border text-center transition-all ${isWinner ? 'bg-amber-400/10 border-amber-400/40 shadow-[0_0_15px_rgba(251,191,36,0.1)]' : 'bg-slate-800/40 border-white/5 opacity-60'}`}>
                                <span className={`text-xl font-black ${isWinner ? 'text-amber-400' : 'text-slate-500'}`}>
                                  {o.offer_data?.wlb_grade || 'N/A'}
                                </span>
                              </div>
                            );
                          })}
                        </div>

                        {/* Benefits Row */}
                        <div className="grid grid-cols-[100px_1fr_1fr] gap-4 items-center">
                          <div className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Benefits</div>
                          {rankedOffers.map(o => {
                            const grades = ['A+', 'A', 'B+', 'B', 'C+', 'C'];
                            const winnerGrade = grades.find(g => rankedOffers.some(ro => ro.offer_data?.benefits_grade === g));
                            const isWinner = o.offer_data?.benefits_grade === winnerGrade;
                            return (
                              <div key={o.offer_id} className={`py-2 rounded-xl border text-center transition-all ${isWinner ? 'bg-amber-400/10 border-amber-400/40 shadow-[0_0_15px_rgba(251,191,36,0.1)]' : 'bg-slate-800/40 border-white/5 opacity-60'}`}>
                                <span className={`text-xl font-black ${isWinner ? 'text-amber-400' : 'text-slate-500'}`}>
                                  {o.offer_data?.benefits_grade || 'N/A'}
                                </span>
                              </div>
                            );
                          })}
                        </div>

                        {/* Growth Row */}
                        <div className="grid grid-cols-[100px_1fr_1fr] gap-4 items-center">
                          <div className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Growth</div>
                          {rankedOffers.map(o => {
                            const grades = ['A+', 'A', 'B+', 'B', 'C+', 'C'];
                            const winnerGrade = grades.find(g => rankedOffers.some(ro => (ro.offer_data?.growth_grade || ro.offer_data?.growth_grade) === g));
                            const isWinner = o.offer_data?.growth_grade === winnerGrade;
                            return (
                              <div key={o.offer_id} className={`py-2 rounded-xl border text-center transition-all ${isWinner ? 'bg-amber-400/10 border-amber-400/40 shadow-[0_0_15px_rgba(251,191,36,0.1)]' : 'bg-slate-800/40 border-white/5 opacity-60'}`}>
                                <span className={`text-xl font-black ${isWinner ? 'text-amber-400' : 'text-slate-500'}`}>
                                  {o.offer_data?.growth_grade || 'N/A'}
                                </span>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white/[0.03] p-8 rounded-3xl border border-white/5">
                  <div className="flex items-center justify-between mb-6">
                    <h5 className="text-sm font-black text-white tracking-[0.3em]">Final Match Index</h5>
                    <div className="flex items-center space-x-2 text-xs font-bold text-slate-500">
                      <InformationCircleIcon className="h-4 w-4" />
                      <span>Match based on your individual weights</span>
                    </div>
                  </div>
                  <div className="space-y-6">
                    {rankedOffers.map((offer, idx) => {
                      const val = offer.total_score || 0;
                      const perc = (val / 100) * 100;
                      const isWinner = offer.rank === 1;
                      return (
                        <div key={offer.offer_id} className="space-y-2">
                          <div className="flex justify-between items-center text-white px-1">
                            <span className="text-base font-black uppercase tracking-tighter">{offer.company}</span>
                            <span className={`text-xl font-black ${isWinner ? 'text-emerald-400' : 'text-slate-400'}`}>{val.toFixed(1)}<span className="text-xs ml-1 opacity-50">% MATCH</span></span>
                          </div>
                          <div className="h-6 w-full bg-slate-900 rounded-2xl overflow-hidden border border-white/[0.05] p-1">
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${Math.max(perc, 5)}%` }}
                              transition={{ duration: 1.2, delay: 0.4, ease: "easeOut" }}
                              className={`h-full rounded-xl ${isWinner ? 'bg-gradient-to-r from-emerald-600 to-emerald-400 shadow-[0_0_25px_rgba(16,185,129,0.4)]' : 'bg-gradient-to-r from-slate-700 to-slate-500 opacity-60'}`}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* Net Value Analysis Table Section */}
            {rankedOffers.length > 0 && (
              <div className="bg-slate-800/20 p-8 rounded-3xl border border-slate-700/30 shadow-2xl backdrop-blur-sm">
                <div className="flex items-center space-x-3 mb-8">
                  <div className="bg-emerald-500/20 p-2.5 rounded-xl border border-emerald-500/40">
                    <CurrencyDollarIcon className="h-6 w-6 text-emerald-400" />
                  </div>
                  <div>
                    <h4 className="text-2xl font-black text-white tracking-tight">Net Value Analysis</h4>
                    <p className="text-slate-500 text-sm font-medium tracking-wide font-mono italic">Detailed financial breakdown</p>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="border-b border-slate-700/50">
                        <th className="py-4 px-6 text-xs font-black text-slate-500 uppercase tracking-[0.2em] w-1/4 min-w-[180px]">Metric Analysis</th>
                        {rankedOffers.map(o => (
                          <th key={o.offer_id} className="py-4 px-6 text-sm font-black text-white uppercase tracking-tighter text-right">{o.company}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/50">
                      {[
                        { label: 'Gross total (inc. equity)', key: 'total_compensation' },
                        { label: 'Estimated tax amount', key: 'estimated_tax' },
                        { label: 'Net take-home', key: 'estimated_net_pay' },
                        { label: 'Annual CoL', key: 'estimated_annual_expenses' },
                        { label: 'Final discretionary income', key: 'net_savings' },
                      ].map((row) => (
                        <tr key={row.key} className="group hover:bg-white/[0.02] transition-colors">
                          <td className="py-5 px-6">
                            <span className="text-sm font-bold text-slate-300 group-hover:text-white transition-colors">{row.label}</span>
                          </td>
                          {rankedOffers.map(o => {
                            const val = o.offer_data?.[row.key] || 0;
                            const maxRowVal = Math.max(...rankedOffers.map(ro => ro.offer_data?.[row.key] || 0), 1);
                            const perc = (val / maxRowVal) * 100;
                            const isWinner = o.rank === 1;
                            return (
                              <td key={o.offer_id} className="py-5 px-6 text-right">
                                <div className="inline-flex flex-col items-end w-full">
                                  <span className="text-[15px] font-black text-white mb-2 font-mono">
                                    ${val.toLocaleString()}
                                  </span>
                                  <div className="h-4 w-32 bg-slate-800 rounded-full overflow-hidden border border-white/5">
                                    <div
                                      className={`h-full rounded-full ${isWinner ? 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.4)]' : 'bg-sky-500/40'}`}
                                      style={{ width: `${Math.max(perc, 5)}%` }}
                                    />
                                  </div>
                                </div>
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                    <tfoot>
                      <tr className="bg-emerald-500/5 border-t-2 border-emerald-500/20">
                        <td className="py-6 px-6">
                          <div className="flex items-center space-x-2">
                            <TrophyIconSolid className="h-5 w-5 text-emerald-400" />
                            <span className="text-sm font-black text-emerald-400 uppercase tracking-widest">Financial Winner</span>
                          </div>
                        </td>
                        {rankedOffers.map(o => {
                          const isWinner = results.final_report?.net_value_analysis?.winner === o.offer_id || o.rank === 1;
                          return (
                            <td key={o.offer_id} className="py-6 px-6 text-right">
                              {isWinner && (
                                <div className="flex flex-row items-center justify-end space-x-3 flex-nowrap">
                                  <div className="text-xl font-black text-emerald-400 tracking-widest whitespace-nowrap">{o.company}</div>
                                  <div className="text-sm font-black text-white bg-emerald-500/20 py-1.5 px-4 rounded-xl border border-emerald-500/30 inline-block uppercase tracking-tighter whitespace-nowrap shadow-lg shadow-emerald-500/10">
                                    Best net value
                                  </div>
                                </div>
                              )}
                            </td>
                          );
                        })}
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </div>
            )}

            {/* How Your Offer Compares (Market Comparison) */}
            {rankedOffers.length > 0 && (
              <div className="bg-slate-800/20 p-8 rounded-3xl border border-slate-700/30 shadow-2xl backdrop-blur-sm overflow-hidden">
                <div className="flex items-center justify-between mb-10">
                  <div className="flex items-center space-x-3">
                    <div className="bg-violet-500/20 p-2.5 rounded-xl border border-violet-500/40">
                      <PresentationChartLineIcon className="h-6 w-6 text-violet-400" />
                    </div>
                    <div>
                      <h4 className="text-2xl font-black text-white tracking-tight capitalize">How your offer compares</h4>
                      <p className="text-slate-500 text-sm font-medium tracking-wide font-mono italic">Benchmarked against market data</p>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {rankedOffers.map((offer) => {
                    const percentile = offer.market_percentile || 50;
                    const median = offer.market_median || (offer.offer_data?.total_compensation || 0) * 0.9;
                    const current = offer.offer_data?.total_compensation || 0;

                    return (
                      <div key={offer.offer_id} className="bg-slate-900/60 rounded-3xl border border-white/5 p-6 hover:border-violet-500/30 transition-all group">
                        <div className="flex justify-between items-start mb-6">
                          <div>
                            <h5 className="text-lg font-black text-white tracking-tighter uppercase">{offer.company}</h5>
                            <p className="text-slate-500 text-xs font-bold uppercase tracking-widest">{offer.position}</p>
                          </div>
                          <div className="text-right">
                            <span className={`block text-2xl font-black tracking-tighter ${percentile >= 70 ? 'text-emerald-400' : percentile >= 40 ? 'text-amber-400' : 'text-rose-400'}`}>
                              {percentile}th
                            </span>
                            <span className="text-[10px] font-black text-slate-600 uppercase tracking-widest">Percentile</span>
                          </div>
                        </div>

                        <div className="space-y-4">
                          <div className="flex justify-between items-end text-[10px] font-black uppercase tracking-widest">
                            <span className="text-slate-500">Market range</span>
                            <div className={`px-2 py-0.5 rounded leading-none ${current > median ? 'text-emerald-400 bg-emerald-400/10' : 'text-rose-400 bg-rose-400/10'}`}>
                              {current > median ? 'Above median' : 'Below median'}
                            </div>
                          </div>

                          <div className="relative pt-6 pb-2">
                            {/* Percentile Bar */}
                            <div className="h-2.5 w-full bg-slate-800 rounded-full relative overflow-hidden">
                              <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${percentile}%` }}
                                transition={{ duration: 1.5, ease: "circOut" }}
                                className={`h-full bg-gradient-to-r ${current > median ? 'from-emerald-600 to-emerald-400' : 'from-rose-600 to-rose-400'}`}
                              />
                            </div>

                            {/* Indicator Pin */}
                            <div
                              className="absolute top-1 -translate-x-1/2 flex flex-col items-center"
                              style={{ left: `${percentile}%` }}
                            >
                              <div className="w-1 h-7 bg-white rounded-full shadow-[0_0_10px_white]" />
                              <div className="text-[9px] font-black text-white mt-1 uppercase whitespace-nowrap bg-slate-900/80 px-1 rounded border border-white/10">Your Offer</div>
                            </div>
                          </div>

                          <div className="flex justify-between items-center bg-slate-950/50 rounded-2xl p-4 border border-white/[0.03]">
                            <div className="text-center flex-1 border-r border-white/5">
                              <div className="text-xs font-bold text-slate-500 uppercase tracking-tighter mb-1">Your Offer</div>
                              <div className="text-base font-black text-white">${current.toLocaleString()}</div>
                            </div>
                            <div className="text-center flex-1">
                              <div className="text-xs font-bold text-slate-500 uppercase tracking-tighter mb-1">Median</div>
                              <div className="text-base font-black text-slate-400">${median.toLocaleString()}</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}


            {/* Lifestyle & Location Comparison Section */}
            {results.final_report?.lifestyle_comparison && (
              <div className="space-y-6">
                <div className="flex items-center space-x-3 mb-2 px-2">
                  <div className="bg-indigo-500/20 p-2.5 rounded-xl border border-indigo-500/40">
                    <MapPinIcon className="h-6 w-6 text-indigo-400" />
                  </div>
                  <h4 className="text-2xl font-black text-white tracking-tight capitalize">Lifestyle & location comparison</h4>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Location Trade-offs Card */}
                  <div className="bg-indigo-950/20 p-8 rounded-3xl border border-indigo-500/20 shadow-xl backdrop-blur-sm self-stretch">
                    <h5 className="text-indigo-400 text-xs font-black uppercase tracking-[0.2em] mb-6 flex items-center">
                      <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 mr-2" />
                      Location Trade-offs
                    </h5>
                    <div className="prose prose-invert prose-indigo max-w-none text-slate-300">
                      <ReactMarkdown
                        components={{
                          p: ({ children }) => <p className="mb-4 leading-relaxed">{children}</p>,
                          ul: ({ children }) => <ul className="space-y-3 mb-4">{children}</ul>,
                          li: ({ children }) => (
                            <li className="flex items-start space-x-3 mb-2">
                              <span className="text-indigo-500 mt-2 w-2 h-2 rounded-full flex-shrink-0 border border-indigo-400/30" />
                              <span className="text-slate-300 leading-relaxed">{children}</span>
                            </li>
                          ),
                          strong: ({ children }) => <span className="text-white font-bold">{children}</span>,
                        }}
                      >
                        {formatMarkdownContent(results.final_report.lifestyle_comparison.location_tradeoffs)}
                      </ReactMarkdown>
                    </div>
                  </div>

                  {/* Hidden Costs Card */}
                  <div className="bg-rose-950/20 p-8 rounded-3xl border border-rose-500/20 shadow-xl backdrop-blur-sm self-stretch">
                    <h5 className="text-rose-400 text-xs font-black uppercase tracking-[0.2em] mb-6 flex items-center">
                      <ExclamationTriangleIconSolid className="h-4 w-4 mr-2" />
                      Hidden Costs to Consider
                    </h5>
                    <div className="prose prose-invert prose-rose max-w-none text-slate-300">
                      <ReactMarkdown
                        components={{
                          p: ({ children }) => <p className="mb-4 leading-relaxed italic text-rose-100/70">{children}</p>,
                          ul: ({ children }) => <ul className="space-y-3 mb-4">{children}</ul>,
                          li: ({ children }) => (
                            <li className="flex items-start space-x-3 mb-2">
                              <span className="text-rose-500 mt-2 w-2 h-2 rounded-full flex-shrink-0 border border-rose-400/30" />
                              <span className="text-slate-300 leading-relaxed">{children}</span>
                            </li>
                          ),
                          strong: ({ children }) => <span className="text-white font-bold">{children}</span>,
                        }}
                      >
                        {formatMarkdownContent(results.final_report.lifestyle_comparison.hidden_costs)}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>
              </div>
            )}


            {/* Key Reasoning Section */}
            {results.final_report?.verdict?.reasoning && Array.isArray(results.final_report.verdict.reasoning) && (
              <div className="space-y-8">
                <div className="flex items-center space-x-3 px-2">
                  <div className="bg-amber-500/20 p-2.5 rounded-xl border border-amber-500/40">
                    <LightBulbIcon className="h-6 w-6 text-amber-400" />
                  </div>
                  <div>
                    <h4 className="text-2xl font-black text-white tracking-tight capitalize">Key reasoning</h4>
                    <p className="text-slate-500 text-sm font-medium tracking-wide italic leading-relaxed">Critical factors behind the recommendation</p>
                  </div>
                </div>

                <div className="bg-slate-900/40 rounded-[2.5rem] border border-white/5 p-8 lg:p-12 relative overflow-hidden">
                  {/* Decorative background split */}
                  <div className="absolute top-0 bottom-0 left-1/2 w-px bg-white/5 hidden lg:block" />

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-x-12 gap-y-10 relative z-10">
                    {results.final_report.verdict.reasoning.map((point: string, idx: number) => {
                      // Split bold title if it exists (e.g., "Title: Description")
                      const parts = point.split(':');
                      const title = parts.length > 1 ? parts[0] : null;
                      const description = parts.length > 1 ? parts.slice(1).join(':') : point;

                      return (
                        <motion.div
                          key={idx}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: idx * 0.1 }}
                          className="flex items-start space-x-5 group"
                        >
                          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-xs font-black text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.1)] group-hover:scale-110 transition-transform">
                            {idx + 1}
                          </div>
                          <div className="space-y-1">
                            {title && (
                              <span className="text-white font-black text-base tracking-tight block">
                                {title}:
                              </span>
                            )}
                            <p className="text-slate-400 text-sm leading-relaxed font-medium">
                              {description.trim()}
                            </p>
                          </div>
                        </motion.div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* Career Growth & Trajectory Section */}
            {rankedOffers.length > 0 && (
              <div className="space-y-8">
                <div className="flex items-center space-x-3 px-2">
                  <div className="bg-violet-500/20 p-2.5 rounded-xl border border-violet-500/40">
                    <FireIcon className="h-6 w-6 text-violet-400" />
                  </div>
                  <div>
                    <h4 className="text-2xl font-black text-white tracking-tight capitalize">Career growth & trajectory</h4>
                    <p className="text-slate-500 text-sm font-medium tracking-wide italic">Long-term potential analysis</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {rankedOffers.map((offer) => (
                    <div key={offer.offer_id} className="bg-slate-900/40 p-8 rounded-[2rem] border border-white/5 relative overflow-hidden group hover:border-violet-500/30 transition-all">
                      <div className="flex justify-between items-start mb-6">
                        <h5 className="text-xl font-black text-white uppercase tracking-tighter">{offer.company}</h5>
                        <div className="flex flex-col items-end">
                          <div className="flex items-center space-x-1.5 bg-violet-500/10 px-3 py-1 rounded-full border border-violet-500/20">
                            <span className="text-[10px] font-black text-violet-400 uppercase tracking-widest leading-none mt-0.5">Growth Score</span>
                            <div className="flex space-x-1">
                              {[1, 2, 3, 4, 5].map((dot) => (
                                <div
                                  key={dot}
                                  className={`w-1.5 h-1.5 rounded-full ${dot <= (offer.offer_data?.growth_score / 2 || 0) ? 'bg-violet-400 shadow-[0_0_8px_rgba(167,139,250,0.6)]' : 'bg-slate-700'}`}
                                />
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <p className="text-slate-400 text-sm leading-relaxed italic font-medium">
                          {offer.offer_data?.growth_description || "Analysis indicates strong long-term potential for skill acquisition and advancement."}
                        </p>

                        {/* Bullet points if available, otherwise fallback */}
                        <div className="pt-4 border-t border-white/5">
                          <ul className="space-y-2">
                            {(offer.offer_data?.growth_points || ['High impact role', 'Clear promotion path', 'Technical mentoring']).map((point: string, pIdx: number) => (
                              <li key={pIdx} className="flex items-center space-x-2 text-[11px] font-bold text-slate-500 uppercase tracking-tight">
                                <CheckCircleIconSolid className="h-3 w-3 text-emerald-500/50" />
                                <span>{point}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Original Verdict & Recommendation Section removed (moved to top) */}
            {/* Fallback to legacy detailed analysis only if no structure */}


            {/* Fallback: Show old Comprehensive Analysis if new structure not available */}
            {!results.final_report?.verdict && results.final_report?.detailed_analysis && (
              <div className="bg-slate-800/30 p-8 rounded-xl border border-slate-700/50">
                <h4 className="text-xl font-bold text-white mb-6 border-b border-slate-700 pb-3">🤖 Comprehensive Analysis</h4>
                <div className="prose prose-invert prose-lg max-w-none text-slate-300">
                  <ReactMarkdown
                    components={{
                      h3: ({ children }) => <h3 className="text-cyan-400 font-semibold mt-6 mb-3">{children}</h3>,
                      ul: ({ children }) => <ul className="list-disc list-inside space-y-2 mb-4">{children}</ul>,
                      li: ({ children }) => <li className="marker:text-slate-500">{children}</li>,
                      strong: ({ children }) => <span className="text-white font-semibold">{children}</span>,
                      p: ({ children }) => <p className="mb-4">{children}</p>
                    }}
                  >
                    {typeof results.final_report?.detailed_analysis === 'string'
                      ? results.final_report.detailed_analysis
                      : String(results.final_report?.detailed_analysis || '')}
                  </ReactMarkdown>
                </div>
              </div>
            )}

            {/* Negotiation Strategy Section - Redesigned with Tabs and Expandable Cards */}
            {(() => {
              const negotiationOptions = results.final_report?.negotiation_options || [];
              const hasOptions = negotiationOptions.length > 0;
              const companies = Array.from(new Set(rankedOffers.map(o => o.company)));

              const currentCompany = selectedNegotiationCompany || companies[0];
              const filteredOptions = negotiationOptions.filter((opt: any) =>
                opt.company === currentCompany || (!opt.company && currentCompany === companies[0])
              );

              if (!hasOptions) return null;

              const copyScript = (script: string, id: string) => {
                navigator.clipboard.writeText(script).then(() => {
                  setCopiedScriptId(id);
                  setTimeout(() => setCopiedScriptId(null), 2000);
                }).catch(() => {
                  console.error('Failed to copy script');
                });
              };

              return (
                <div className="space-y-8">
                  <div className="flex items-center space-x-3 px-2">
                    <div className="bg-amber-500/20 p-2.5 rounded-xl border border-amber-500/40">
                      <UserGroupIcon className="h-6 w-6 text-amber-400" />
                    </div>
                    <div>
                      <h4 className="text-2xl font-black text-white tracking-tight capitalize">Negotiation strategy</h4>
                      <p className="text-slate-500 text-sm font-medium tracking-wide">Tactical scripts to maximize your offer value</p>
                    </div>
                  </div>

                  {/* Company Selection Tabs */}
                  {companies.length > 1 && (
                    <div className="flex p-1 bg-slate-900/60 rounded-2xl border border-white/5 w-fit">
                      {companies.map((company) => (
                        <button
                          key={company}
                          onClick={() => setSelectedNegotiationCompany(company)}
                          className={`px-6 py-2.5 rounded-xl text-xs font-black uppercase tracking-widest transition-all duration-300 ${currentCompany === company
                            ? 'bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/20'
                            : 'text-slate-500 hover:text-white'
                            }`}
                        >
                          {company}
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Options List */}
                  <div className="space-y-4">
                    {filteredOptions.length > 0 ? (
                      filteredOptions.map((option: any) => {
                        const difficulty = option.difficulty || 'worth_asking';
                        const isSelected = selectedNegotiationOption === option.id;

                        return (
                          <div
                            key={option.id}
                            className={`group relative overflow-hidden rounded-[2rem] border transition-all duration-500 ${isSelected
                              ? 'bg-slate-900 border-amber-500/50 shadow-2xl scale-[1.01]'
                              : 'bg-slate-900/40 border-white/5 hover:border-white/10'
                              }`}
                          >
                            <div
                              className="p-8 cursor-pointer relative z-10"
                              onClick={() => setSelectedNegotiationOption(isSelected ? null : option.id)}
                            >
                              <div className="flex items-start justify-between">
                                <div className="space-y-3 flex-1 pr-6">
                                  <div className="flex items-center space-x-3">
                                    <span className="px-3 py-1 rounded-full bg-slate-800 border border-white/5 text-[10px] font-black text-slate-400 uppercase tracking-widest">
                                      {option.difficulty_label || difficulty.replace('_', ' ')}
                                    </span>
                                    {option.financial_impact && (
                                      <span className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-[10px] font-black text-emerald-400 uppercase tracking-widest">
                                        {option.financial_impact} IMPACT
                                      </span>
                                    )}
                                  </div>
                                  <h5 className="text-xl font-black text-white uppercase tracking-tighter group-hover:text-amber-400 transition-colors">
                                    {option.title}
                                  </h5>
                                </div>
                                <div className={`p-2 rounded-full border border-white/5 transition-transform duration-500 ${isSelected ? 'rotate-180 bg-amber-500 text-slate-950' : 'text-slate-500'}`}>
                                  <ChevronDownIcon className="h-5 w-5" />
                                </div>
                              </div>
                            </div>

                            {/* Expanded Content */}
                            <motion.div
                              initial={false}
                              animate={{ height: isSelected ? 'auto' : 0, opacity: isSelected ? 1 : 0 }}
                              className="overflow-hidden bg-white/[0.02]"
                            >
                              <div className="p-8 pt-0 border-t border-white/5">
                                <div className="space-y-6 pt-6">
                                  <div className="space-y-2">
                                    <h6 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">The Strategy</h6>
                                    <p className="text-slate-300 text-sm leading-relaxed font-medium">
                                      {option.description}
                                    </p>
                                  </div>

                                  <div className="space-y-3">
                                    <div className="flex items-center justify-between">
                                      <h6 className="text-[10px] font-black text-emerald-500 uppercase tracking-[0.2em]">Negotiation Script</h6>
                                      <button
                                        onClick={(e) => { e.stopPropagation(); copyScript(option.script, option.id); }}
                                        className={`text-[10px] font-black uppercase tracking-widest underline underline-offset-4 transition-colors ${copiedScriptId === option.id ? 'text-emerald-400' : 'text-slate-400 hover:text-white'}`}
                                      >
                                        {copiedScriptId === option.id ? 'Copied!' : 'Copy Script'}
                                      </button>
                                    </div>
                                    <div className="bg-slate-950/80 rounded-2xl p-6 border border-white/5 group-relative">
                                      <p className="text-emerald-50/80 text-sm font-mono leading-loose">
                                        {option.script}
                                      </p>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </motion.div>
                          </div>
                        );
                      })
                    ) : (
                      <div className="text-center py-12 bg-slate-900/20 border border-dashed border-white/5 rounded-3xl">
                        <p className="text-slate-500 text-sm font-black uppercase tracking-widest">No strategies found for this company</p>
                      </div>
                    )}
                  </div>
                </div>
              );
            })()}

            {/* Decision Framework Section (keep for backward compatibility) */}
            {results.final_report?.decision_framework && (
              <div className="bg-slate-800/30 p-8 rounded-xl border border-slate-700/50">
                <h4 className="text-xl font-bold text-white mb-6 border-b border-slate-700 pb-3">📋 Decision Framework</h4>
                <div className="prose prose-invert prose-lg max-w-none text-slate-300">
                  <ReactMarkdown
                    components={{
                      h3: ({ children }) => <h3 className="text-emerald-400 font-semibold mt-6 mb-3">{children}</h3>,
                      ul: ({ children }) => <ul className="list-disc list-inside space-y-2 mb-4">{children}</ul>,
                      li: ({ children }) => <li className="marker:text-slate-500">{children}</li>,
                      strong: ({ children }) => <span className="text-white font-semibold">{children}</span>,
                      p: ({ children }) => <p className="mb-4">{children}</p>
                    }}
                  >
                    {(() => {
                      const framework = results.final_report?.decision_framework;
                      if (typeof framework === 'string') {
                        // Convert comma-separated list to markdown list if needed
                        if (framework.includes(',') && !framework.includes('\n') && !framework.includes('-')) {
                          return framework.split(',').map(item => item.trim()).filter(Boolean).map(item => `- ${item}`).join('\n');
                        }
                        return framework;
                      }
                      return String(framework || '');
                    })()}
                  </ReactMarkdown>
                </div>
              </div>
            )}

            {/* Visual Dashboard Loop */}
            <div className="space-y-8">
              <h4 className="text-xl font-bold text-white mb-6 border-b border-slate-700 pb-3 capitalize italic px-2">Interactive smart dashboard</h4>
              {rankedOffers.map((offer) => (
                <VisualDashboard
                  key={offer.offer_id}
                  offer={offer}
                  analysis={offer.ai_recommendation}
                />
              ))}
            </div>
          </motion.div>
        )}

        {
          activeTab === 'charts' && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="grid grid-cols-1 lg:grid-cols-2 gap-8"
            >
              {/* Radar Chart */}
              <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg">
                <h4 className="text-lg font-bold text-white mb-6">Multi-Dimensional Analysis</h4>
                <div className="h-[400px] flex items-center justify-center relative">
                  <Radar
                    data={radarData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        r: {
                          beginAtZero: true,
                          min: 0,
                          max: 10,
                          ticks: {
                            display: true,
                            stepSize: 2,
                            color: '#94a3b8',
                            font: { size: 11 },
                            backdropColor: 'rgba(15, 23, 42, 0.8)',
                            backdropPadding: 4
                          },
                          grid: {
                            color: 'rgba(255, 255, 255, 0.15)',
                            lineWidth: 1
                          },
                          angleLines: {
                            color: 'rgba(255, 255, 255, 0.1)',
                            lineWidth: 1
                          },
                          pointLabels: {
                            color: '#cbd5e1',
                            font: { size: 12, weight: 500 }
                          }
                        }
                      },
                      plugins: {
                        legend: {
                          position: 'bottom',
                          labels: { color: '#e2e8f0', padding: 20, usePointStyle: true }
                        },
                        tooltip: {
                          callbacks: {
                            label: (context) => {
                              return `${context.dataset.label}: ${context.parsed.r}/10`
                            }
                          }
                        }
                      }
                    }}
                  />
                </div>
                <div className="text-xs text-slate-500 mt-2 text-center">
                  Scale: 0-10 (higher is better)
                </div>
              </div>

              {/* Stacked Bar Chart */}
              <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg">
                <h4 className="text-lg font-bold text-white mb-6">Cost-Adjusted Compensation Breakdown</h4>
                <div className="h-[400px]">
                  <Bar
                    data={barData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        x: {
                          grid: { display: false },
                          ticks: { color: '#94a3b8' }
                        },
                        y: {
                          grid: { color: 'rgba(255, 255, 255, 0.05)' },
                          ticks: {
                            color: '#94a3b8',
                            callback: (value) => '$' + Number(value) / 1000 + 'k'
                          }
                        }
                      },
                      plugins: {
                        legend: {
                          position: 'bottom',
                          labels: { color: '#e2e8f0', padding: 20, usePointStyle: true }
                        },
                        tooltip: {
                          callbacks: {
                            label: (context) => {
                              let label = context.dataset.label || '';
                              if (label) {
                                label += ': ';
                              }
                              if (context.parsed.y !== null) {
                                label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed.y);
                              }
                              return label;
                            }
                          }
                        }
                      }
                    }}
                  />
                </div>
              </div>

              {/* Detailed Metrics Table Section within Charts Tab for Dashboard View */}
              <div className="lg:col-span-2 bg-slate-800 rounded-xl border border-slate-700 shadow-lg overflow-hidden mt-4">
                <div className="p-6 border-b border-slate-700">
                  <h4 className="text-lg font-bold text-white">Detailed Metrics Comparison (Including Cost of Living)</h4>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead>
                      <tr className="bg-slate-900/50 border-b border-slate-700">
                        <th className="p-4 text-slate-400 font-medium">Metric</th>
                        {rankedOffers.map(o => (
                          <th key={o.offer_id} className="p-4 text-white font-semibold">{o.company}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700">
                      {[
                        { label: 'Base Salary', key: 'base_salary', format: 'currency', color: 'text-red-400' },
                        { label: 'Equity', key: 'equity', format: 'currency', color: 'text-amber-400' },
                        { label: 'Bonus', key: 'bonus', format: 'currency', color: 'text-emerald-400' },
                        { label: 'Total Comp', key: 'total_compensation', format: 'currency', color: 'text-white font-bold' },
                        {
                          label: 'Estimated Net Pay',
                          key: 'estimated_net_pay',
                          format: 'currency',
                          color: 'text-emerald-300 font-semibold',
                          tooltip: 'Estimated take-home pay after Federal, State, and FICA taxes based on location.'
                        },
                        {
                          label: 'Estimated Annual Expenses',
                          key: 'estimated_annual_expenses',
                          format: 'currency',
                          color: 'text-red-300',
                          tooltip: 'Estimated basic living expenses for a single person in this location.'
                        },
                        {
                          label: 'Net Savings',
                          key: 'net_savings',
                          format: 'currency',
                          color: 'text-cyan-300 font-bold',
                          tooltip: 'Estimated potential savings (Net Pay - Annual Expenses).'
                        },
                        { label: 'Job Level', key: 'level', format: 'text', color: 'text-slate-200' },
                        // Add more metrics as needed
                      ].map((row, idx) => (
                        <tr key={idx} className="hover:bg-slate-700/30 transition-colors">
                          <td className="p-4 text-slate-300 flex items-center space-x-2">
                            <span>{row.label}</span>
                            {row.tooltip && (
                              <div className="group relative">
                                <span className="cursor-help text-slate-500 hover:text-cyan-400 transition-colors">ℹ️</span>
                                <div className="absolute left-full ml-2 top-1/2 -translate-y-1/2 w-48 p-2 bg-slate-950 border border-slate-700 rounded text-xs text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 shadow-lg">
                                  {row.tooltip}
                                </div>
                              </div>
                            )}
                          </td>
                          {rankedOffers.map(o => {
                            const val = o.offer_data?.[row.key] || 0;
                            const display = row.format === 'currency'
                              ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val)
                              : val;
                            return (
                              <td key={o.offer_id} className={`p-4 ${row.color}`}>
                                {display}
                              </td>
                            )
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </motion.div>
          )
        }

        {/* Timeline Tab */}
        {
          activeTab === 'timeline' && (
            <div className="text-center py-20">
              <ClockIcon className="h-16 w-16 text-slate-600 mx-auto mb-4" />
              <h4 className="text-lg font-bold text-white mb-2">Decision Timeline</h4>
              <p className="text-slate-400">Coming soon in the next update.</p>
            </div>
          )
        }

      </div >
    </motion.div >
  )
}
