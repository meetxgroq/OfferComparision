'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  SparklesIcon,
  ChartBarIcon,
  TableCellsIcon,
  ClockIcon,
  DocumentArrowDownIcon,
  ChevronDownIcon
} from '@heroicons/react/24/outline'
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
            {/* Verdict & Recommendation Section (replaces AI Recommends & Exec Summary) */}
            {results.final_report?.verdict && (
              <div className="bg-slate-800/30 p-8 rounded-xl border border-slate-700/50 mb-8">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="bg-purple-600/20 p-2 rounded-lg border border-purple-500/50">
                    <span className="text-2xl">🎯</span>
                  </div>
                  <h4 className="text-xl font-bold text-white">Verdict & Recommendation</h4>
                </div>

                {/* Recommended Offer Badge */}
                {results.final_report.verdict.recommended_company && (
                  <div className="mb-6 bg-gradient-to-r from-purple-600/20 to-blue-600/20 border border-purple-500/30 rounded-lg p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-purple-300 text-sm font-medium mb-1">Recommended Offer</p>
                        <p className="text-white text-3xl font-bold">
                          {results.final_report.verdict.recommended_company}
                        </p>
                        {results.final_report.verdict.financial_superiority && (
                          <p className="text-green-400 text-sm mt-2">
                            ✓ Financially Superior
                          </p>
                        )}
                      </div>
                      <div className="bg-purple-600/30 px-4 py-2 rounded-lg border border-purple-500/50">
                        <span className="text-purple-200 text-4xl">🏆</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Reasoning */}
                {results.final_report.verdict.reasoning && Array.isArray(results.final_report.verdict.reasoning) && (
                  <div className="mb-6">
                    <h5 className="text-lg font-semibold text-cyan-400 mb-4">Key Reasoning</h5>
                    <ul className="space-y-3">
                      {results.final_report.verdict.reasoning.map((point: string, idx: number) => (
                        <li key={idx} className="flex items-start space-x-3">
                          <span className="text-green-400 text-xl mt-1">✓</span>
                          <span className="text-slate-300 flex-1">{point}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Career Growth Considerations */}
                {results.final_report.verdict.career_growth_considerations && (
                  <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-4">
                    <h5 className="text-lg font-semibold text-emerald-400 mb-2">Career Growth Considerations</h5>
                    <p className="text-slate-300">
                      {typeof results.final_report.verdict.career_growth_considerations === 'string'
                        ? results.final_report.verdict.career_growth_considerations
                        : String(results.final_report.verdict.career_growth_considerations || '')}
                    </p>
                  </div>
                )}
              </div>
            )}


            {/* Comprehensive Metric Comparison - Bar Charts (Compact) */}
            {rankedOffers.length > 0 && (
              <div className="bg-slate-800/30 p-6 rounded-xl border border-slate-700/50">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="bg-blue-600/20 p-2 rounded-lg border border-blue-500/50">
                    <ChartBarIcon className="h-5 w-5 text-blue-400" />
                  </div>
                  <div>
                    <h4 className="text-lg font-bold text-white">Comprehensive Offer Comparison</h4>
                    <p className="text-slate-400 text-xs mt-0.5">Side-by-side metric analysis</p>
                  </div>
                </div>

                <div className="space-y-6">
                  {/* Base Salary Comparison */}
                  <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-4">
                    <h5 className="text-sm font-semibold text-white mb-2">Base Salary</h5>
                    <div className="space-y-2">
                      {rankedOffers.map((offer, idx) => {
                        const value = offer.offer_data?.base_salary || 0;
                        const maxValue = Math.max(...rankedOffers.map(o => o.offer_data?.base_salary || 0));
                        const percentage = maxValue > 0 ? (value / maxValue) * 100 : 0;
                        const colors = ['bg-cyan-500', 'bg-orange-500', 'bg-purple-500', 'bg-green-500'];
                        const color = colors[idx % colors.length];

                        return (
                          <div key={offer.offer_id || idx} className="flex items-center gap-4">
                            <div className="w-28 flex-shrink-0">
                              <span className="text-slate-300 text-xs font-medium">{offer.company}</span>
                            </div>
                            <div className="flex-1 relative">
                              <div className="w-full bg-slate-700 rounded-full h-4 relative overflow-hidden">
                                <div
                                  className={`${color} h-4 rounded-full transition-all duration-500 flex items-center justify-end pr-2`}
                                  style={{ width: `${Math.max(percentage, 5)}%` }}
                                >
                                  <span className="text-white text-[10px] font-bold drop-shadow-md">${value.toLocaleString()}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Total Compensation Comparison */}
                  <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-4">
                    <h5 className="text-sm font-semibold text-white mb-2">Total Compensation</h5>
                    <div className="space-y-2">
                      {rankedOffers.map((offer, idx) => {
                        const value = offer.offer_data?.total_compensation || 0;
                        const maxValue = Math.max(...rankedOffers.map(o => o.offer_data?.total_compensation || 0));
                        const percentage = maxValue > 0 ? (value / maxValue) * 100 : 0;
                        const colors = ['bg-cyan-500', 'bg-orange-500', 'bg-purple-500', 'bg-green-500'];
                        const color = colors[idx % colors.length];

                        return (
                          <div key={offer.offer_id || idx} className="flex items-center gap-4">
                            <div className="w-28 flex-shrink-0">
                              <span className="text-slate-300 text-xs font-medium">{offer.company}</span>
                            </div>
                            <div className="flex-1 relative">
                              <div className="w-full bg-slate-700 rounded-full h-4 relative overflow-hidden">
                                <div
                                  className={`${color} h-4 rounded-full transition-all duration-500 flex items-center justify-end pr-2`}
                                  style={{ width: `${Math.max(percentage, 5)}%` }}
                                >
                                  <span className="text-white text-[10px] font-bold drop-shadow-md">${value.toLocaleString()}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Equity Comparison */}
                  <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-4">
                    <h5 className="text-sm font-semibold text-white mb-2">Equity Value</h5>
                    <div className="space-y-2">
                      {rankedOffers.map((offer, idx) => {
                        const value = offer.offer_data?.equity || 0;
                        const maxValue = Math.max(...rankedOffers.map(o => o.offer_data?.equity || 0));
                        const percentage = maxValue > 0 ? (value / maxValue) * 100 : 0;
                        const colors = ['bg-cyan-500', 'bg-orange-500', 'bg-purple-500', 'bg-green-500'];
                        const color = colors[idx % colors.length];

                        return (
                          <div key={offer.offer_id || idx} className="flex items-center gap-4">
                            <div className="w-28 flex-shrink-0">
                              <span className="text-slate-300 text-xs font-medium">{offer.company}</span>
                            </div>
                            <div className="flex-1 relative">
                              <div className="w-full bg-slate-700 rounded-full h-4 relative overflow-hidden">
                                <div
                                  className={`${color} h-4 rounded-full transition-all duration-500 flex items-center justify-end pr-2`}
                                  style={{ width: `${Math.max(percentage, 5)}%` }}
                                >
                                  <span className="text-white text-[10px] font-bold drop-shadow-md">${value.toLocaleString()}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Bonus Comparison */}
                  <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-4">
                    <h5 className="text-sm font-semibold text-white mb-2">Bonus</h5>
                    <div className="space-y-2">
                      {rankedOffers.map((offer, idx) => {
                        const value = offer.offer_data?.bonus || 0;
                        const maxValue = Math.max(...rankedOffers.map(o => o.offer_data?.bonus || 0));
                        const percentage = maxValue > 0 ? (value / maxValue) * 100 : 0;
                        const colors = ['bg-cyan-500', 'bg-orange-500', 'bg-purple-500', 'bg-green-500'];
                        const color = colors[idx % colors.length];

                        return (
                          <div key={offer.offer_id || idx} className="flex items-center gap-4">
                            <div className="w-28 flex-shrink-0">
                              <span className="text-slate-300 text-xs font-medium">{offer.company}</span>
                            </div>
                            <div className="flex-1 relative">
                              <div className="w-full bg-slate-700 rounded-full h-4 relative overflow-hidden">
                                <div
                                  className={`${color} h-4 rounded-full transition-all duration-500 flex items-center justify-end pr-2`}
                                  style={{ width: `${Math.max(percentage, 5)}%` }}
                                >
                                  <span className="text-white text-[10px] font-bold drop-shadow-md">${value.toLocaleString()}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Work-Life Balance Score */}
                  <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-4">
                    <h5 className="text-sm font-semibold text-white mb-2">Work-Life Balance Score</h5>
                    <div className="space-y-2">
                      {rankedOffers.map((offer, idx) => {
                        const value = offer.offer_data?.wlb_score || 0;
                        const maxValue = 10; // WLB score is typically 0-10
                        const percentage = maxValue > 0 ? (value / maxValue) * 100 : 0;
                        const colors = ['bg-cyan-500', 'bg-orange-500', 'bg-purple-500', 'bg-green-500'];
                        const color = colors[idx % colors.length];

                        return (
                          <div key={offer.offer_id || idx} className="flex items-center gap-4">
                            <div className="w-28 flex-shrink-0">
                              <span className="text-slate-300 text-xs font-medium">{offer.company}</span>
                            </div>
                            <div className="flex-1 relative">
                              <div className="w-full bg-slate-700 rounded-full h-4 relative overflow-hidden">
                                <div
                                  className={`${color} h-4 rounded-full transition-all duration-500 flex items-center justify-end pr-2`}
                                  style={{ width: `${Math.max(percentage, 5)}%` }}
                                >
                                  <span className="text-white text-[10px] font-bold drop-shadow-md">{value}/10</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Growth Score */}
                  <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-4">
                    <h5 className="text-sm font-semibold text-white mb-2">Growth Potential Score</h5>
                    <div className="space-y-2">
                      {rankedOffers.map((offer, idx) => {
                        const value = offer.offer_data?.growth_score || 0;
                        const maxValue = 10; // Growth score is typically 0-10
                        const percentage = maxValue > 0 ? (value / maxValue) * 100 : 0;
                        const colors = ['bg-cyan-500', 'bg-orange-500', 'bg-purple-500', 'bg-green-500'];
                        const color = colors[idx % colors.length];

                        return (
                          <div key={offer.offer_id || idx} className="flex items-center gap-4">
                            <div className="w-28 flex-shrink-0">
                              <span className="text-slate-300 text-xs font-medium">{offer.company}</span>
                            </div>
                            <div className="flex-1 relative">
                              <div className="w-full bg-slate-700 rounded-full h-4 relative overflow-hidden">
                                <div
                                  className={`${color} h-4 rounded-full transition-all duration-500 flex items-center justify-end pr-2`}
                                  style={{ width: `${Math.max(percentage, 5)}%` }}
                                >
                                  <span className="text-white text-[10px] font-bold drop-shadow-md">{value}/10</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Benefits Grade */}
                  <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-4">
                    <h5 className="text-sm font-semibold text-white mb-2">Benefits Grade</h5>
                    <div className="space-y-2">
                      {rankedOffers.map((offer, idx) => {
                        const grade = offer.offer_data?.benefits_grade || 'N/A';
                        // Convert grade to numeric value for visualization
                        const gradeMap: { [key: string]: number } = {
                          'A+': 100, 'A': 90, 'A-': 85,
                          'B+': 80, 'B': 75, 'B-': 70,
                          'C+': 65, 'C': 60, 'C-': 55,
                          'D': 50, 'F': 25, 'N/A': 0
                        };
                        const value = gradeMap[grade] || 0;
                        const percentage = value;
                        const colors = ['bg-cyan-500', 'bg-orange-500', 'bg-purple-500', 'bg-green-500'];
                        const color = colors[idx % colors.length];

                        return (
                          <div key={offer.offer_id || idx} className="flex items-center gap-4">
                            <div className="w-28 flex-shrink-0">
                              <span className="text-slate-300 text-xs font-medium">{offer.company}</span>
                            </div>
                            <div className="flex-1 relative">
                              <div className="w-full bg-slate-700 rounded-full h-4 relative overflow-hidden">
                                <div
                                  className={`${color} h-4 rounded-full transition-all duration-500 flex items-center justify-end pr-2`}
                                  style={{ width: `${Math.max(percentage, 5)}%` }}
                                >
                                  <span className="text-white text-[10px] font-bold drop-shadow-md">{grade}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Total Score */}
                  <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-4">
                    <h5 className="text-sm font-semibold text-white mb-2">Overall Score</h5>
                    <div className="space-y-2">
                      {rankedOffers.map((offer, idx) => {
                        const value = offer.total_score || 0;
                        const maxValue = 100; // Total score is typically 0-100
                        const percentage = maxValue > 0 ? (value / maxValue) * 100 : 0;
                        const colors = ['bg-cyan-500', 'bg-orange-500', 'bg-purple-500', 'bg-green-500'];
                        const color = colors[idx % colors.length];

                        return (
                          <div key={offer.offer_id || idx} className="flex items-center gap-4">
                            <div className="w-28 flex-shrink-0">
                              <span className="text-slate-300 text-xs font-medium">{offer.company}</span>
                            </div>
                            <div className="flex-1 relative">
                              <div className="w-full bg-slate-700 rounded-full h-4 relative overflow-hidden">
                                <div
                                  className={`${color} h-4 rounded-full transition-all duration-500 flex items-center justify-end pr-2`}
                                  style={{ width: `${Math.max(percentage, 5)}%` }}
                                >
                                  <span className="text-white text-[10px] font-bold drop-shadow-md">{value.toFixed(1)}/100</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </div>
            )}


            {/* Lifestyle & Location Comparison Section */}
            {results.final_report?.lifestyle_comparison && (
              <div className="bg-slate-800/30 p-8 rounded-xl border border-slate-700/50">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="bg-blue-600/20 p-2 rounded-lg border border-blue-500/50">
                    <span className="text-2xl">🌍</span>
                  </div>
                  <h4 className="text-xl font-bold text-white">Lifestyle & Location Comparison</h4>
                </div>

                {results.final_report.lifestyle_comparison.location_tradeoffs && (
                  <div className="mb-6">
                    <h5 className="text-lg font-semibold text-cyan-400 mb-3">Location Trade-offs</h5>
                    <div className="prose prose-invert prose-lg max-w-none text-slate-300">
                      <ReactMarkdown
                        components={{
                          p: ({ children }) => <p className="mb-4">{children}</p>,
                          ul: ({ children }) => <ul className="list-disc list-inside space-y-2 mb-4">{children}</ul>,
                          li: ({ children }) => <li className="marker:text-slate-500">{children}</li>,
                          strong: ({ children }) => <span className="text-white font-semibold">{children}</span>,
                        }}
                      >
                        {typeof results.final_report.lifestyle_comparison.location_tradeoffs === 'string'
                          ? results.final_report.lifestyle_comparison.location_tradeoffs
                          : String(results.final_report.lifestyle_comparison.location_tradeoffs || '')}
                      </ReactMarkdown>
                    </div>
                  </div>
                )}

                {results.final_report.lifestyle_comparison.hidden_costs && (
                  <div className="bg-amber-900/20 border border-amber-500/30 rounded-lg p-4">
                    <div className="flex items-start space-x-3">
                      <span className="text-amber-400 text-xl">⚠️</span>
                      <div>
                        <h5 className="text-lg font-semibold text-amber-300 mb-2">Hidden Costs to Consider</h5>
                        <div className="prose prose-invert text-slate-300">
                          <ReactMarkdown
                            components={{
                              p: ({ children }) => <p className="mb-2">{children}</p>,
                              ul: ({ children }) => <ul className="list-disc list-inside space-y-1">{children}</ul>,
                              li: ({ children }) => <li className="marker:text-amber-500">{children}</li>,
                            }}
                          >
                            {typeof results.final_report.lifestyle_comparison.hidden_costs === 'string'
                              ? results.final_report.lifestyle_comparison.hidden_costs
                              : String(results.final_report.lifestyle_comparison.hidden_costs || '')}
                          </ReactMarkdown>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
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

            {/* Negotiation Opportunities Section - Interactive Options */}
            {(() => {
              const negotiationOptions = results.final_report?.negotiation_options || [];
              const hasOptions = negotiationOptions.length > 0;

              // Fallback to simple list if structured options not available
              const simpleOpportunities = results.final_report?.negotiation_opportunities || [];
              const hasSimpleList = !hasOptions && Array.isArray(simpleOpportunities) && simpleOpportunities.length > 0;

              if (!hasOptions && !hasSimpleList) return null;

              const copyScript = (script: string) => {
                navigator.clipboard.writeText(script).then(() => {
                  alert('Script copied to clipboard!');
                }).catch(() => {
                  alert('Failed to copy script');
                });
              };

              const selectedOption = negotiationOptions.find((opt: any) => opt.id === selectedNegotiationOption);

              return (
                <div className="bg-gradient-to-br from-amber-900/20 to-slate-900 p-8 rounded-xl border border-amber-500/30 shadow-lg">
                  <div className="flex items-center space-x-3 mb-6">
                    <div className="bg-amber-600/20 p-2 rounded-lg border border-amber-500/50">
                      <span className="text-2xl">💼</span>
                    </div>
                    <h4 className="text-xl font-bold text-amber-100">Negotiation Opportunities</h4>
                  </div>

                  {hasOptions ? (
                    <div className="space-y-4 mb-6">
                      {negotiationOptions.map((option: any) => {
                        const difficultyColors = {
                          'likely_achievable': { bg: 'bg-green-600/20', text: 'text-green-400', border: 'border-green-500/50' },
                          'worth_asking': { bg: 'bg-orange-600/20', text: 'text-orange-400', border: 'border-orange-500/50' },
                          'ambitious_ask': { bg: 'bg-red-600/20', text: 'text-red-400', border: 'border-red-500/50' }
                        };
                        const colors = difficultyColors[option.difficulty as keyof typeof difficultyColors] || difficultyColors.worth_asking;
                        const isSelected = selectedNegotiationOption === option.id;

                        return (
                          <div
                            key={option.id}
                            onClick={() => setSelectedNegotiationOption(isSelected ? null : option.id)}
                            className={`border rounded-lg overflow-hidden transition-all duration-300 ${isSelected
                              ? 'border-cyan-500 bg-cyan-900/20 shadow-lg shadow-cyan-500/20'
                              : 'border-slate-700 hover:border-slate-600 bg-slate-800/30'
                              }`}
                          >
                            {/* Header */}
                            <div className="p-4 flex items-center justify-between cursor-pointer">
                              <div className="flex-1 pr-4">
                                <div className="flex items-center gap-3 mb-2">
                                  <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider ${colors.bg} ${colors.text} border ${colors.border}`}>
                                    {option.difficulty_label || option.difficulty}
                                  </span>
                                </div>
                                <h5 className="text-white font-semibold">{option.title}</h5>
                                <p className="text-slate-400 text-sm mt-1 line-clamp-1">{option.description}</p>
                              </div>
                              <ChevronDownIcon
                                className={`w-5 h-5 text-slate-400 transition-transform duration-300 ${isSelected ? 'rotate-180' : ''}`}
                              />
                            </div>

                            {/* Expanded Content */}
                            <div className={`grid transition-all duration-300 ease-in-out ${isSelected ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'}`}>
                              <div className="overflow-hidden">
                                <div className="p-4 pt-0 border-t border-slate-700/50">
                                  {/* Full Description */}
                                  <p className="text-slate-300 text-sm mb-4 leading-relaxed">{option.description}</p>

                                  <div className="flex items-center justify-between mb-2">
                                    <h6 className="text-cyan-400 text-xs font-bold uppercase tracking-wider">Negotiation Script</h6>
                                    <button
                                      onClick={(e) => { e.stopPropagation(); copyScript(option.script); }}
                                      className="px-2 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded text-xs text-slate-300 hover:text-white transition-colors flex items-center gap-1"
                                    >
                                      <DocumentArrowDownIcon className="h-3 w-3" />
                                      Copy
                                    </button>
                                  </div>
                                  <div className="bg-slate-950/80 border border-slate-800 rounded p-3 text-slate-300 text-sm whitespace-pre-wrap font-mono relative">
                                    {option.script}
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    // Fallback: Show simple list if structured options not available
                    <div className="space-y-4">
                      {simpleOpportunities.map((opportunity: string, idx: number) => (
                        <div key={idx} className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 flex items-start space-x-3">
                          <div className="bg-amber-600/20 p-1.5 rounded border border-amber-500/50 flex-shrink-0 mt-0.5">
                            <span className="text-amber-400 font-bold">{idx + 1}</span>
                          </div>
                          <p className="text-slate-300 flex-1">{opportunity}</p>
                        </div>
                      ))}
                    </div>
                  )}
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
              <h4 className="text-xl font-bold text-white mb-6 border-b border-slate-700 pb-3">🎯 Smart Analysis Dashboard</h4>
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

        {activeTab === 'charts' && (
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
                          font: { size: 12, weight: '500' }
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
        )}

        {/* Timeline Tab */}
        {activeTab === 'timeline' && (
          <div className="text-center py-20">
            <ClockIcon className="h-16 w-16 text-slate-600 mx-auto mb-4" />
            <h4 className="text-lg font-bold text-white mb-2">Decision Timeline</h4>
            <p className="text-slate-400">Coming soon in the next update.</p>
          </div>
        )}

      </div>
    </motion.div>
  )
}
