'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  SparklesIcon,
  ChartBarIcon,
  TableCellsIcon,
  ClockIcon,
  DocumentArrowDownIcon
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
    labels: ['Salary', 'Equity', 'Bonus', 'Benefits', 'Work-Life', 'Growth', 'Role Fit', 'Overall'],
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
        offer.offer_data?.role_fit || 0,
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
            {/* Executive Summary - Styled Distinctly */}
            <div className="bg-gradient-to-br from-indigo-900/40 to-slate-900 p-8 rounded-xl border border-indigo-500/30 shadow-lg">
              <div className="flex items-center space-x-3 mb-6">
                <div className="bg-indigo-600/20 p-2 rounded-lg border border-indigo-500/50">
                  <SparklesIcon className="h-6 w-6 text-indigo-400" />
                </div>
                <h4 className="text-xl font-bold text-indigo-100">Executive Summary</h4>
              </div>
              <div className="text-slate-300 leading-relaxed text-lg">
                <ReactMarkdown
                  components={{
                    p: ({ children }) => <p className="mb-4">{children}</p>,
                    strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,
                  }}
                >
                  {results.executive_summary}
                </ReactMarkdown>
              </div>
            </div>

            {/* AI Analysis Section */}
            <div className="bg-slate-800/30 p-8 rounded-xl border border-slate-700/50">
              <h4 className="text-xl font-bold text-white mb-6 border-b border-slate-700 pb-3">🤖 Comprehensive Analysis</h4>
              <div className="prose prose-invert prose-lg max-w-none text-slate-300">
                <ReactMarkdown
                  components={{
                    h3: ({ children }) => <h3 className="text-cyan-400 font-semibold mt-6 mb-3">{children}</h3>,
                    ul: ({ children }) => <ul className="list-disc list-inside space-y-2 mb-4">{children}</ul>,
                    li: ({ children }) => <li className="marker:text-slate-500">{children}</li>,
                    strong: ({ children }) => <span className="text-white font-semibold">{children}</span>
                  }}
                >
                  {results.final_report?.detailed_analysis}
                </ReactMarkdown>
              </div>
            </div>

            {/* Decision Framework Section */}
            <div className="bg-slate-800/30 p-8 rounded-xl border border-slate-700/50">
              <h4 className="text-xl font-bold text-white mb-6 border-b border-slate-700 pb-3">📋 Decision Framework</h4>
              <div className="prose prose-invert prose-lg max-w-none text-slate-300">
                <ReactMarkdown
                  components={{
                    h3: ({ children }) => <h3 className="text-emerald-400 font-semibold mt-6 mb-3">{children}</h3>,
                    ul: ({ children }) => <ul className="list-disc list-inside space-y-2 mb-4">{children}</ul>,
                    li: ({ children }) => <li className="marker:text-slate-500">{children}</li>,
                    strong: ({ children }) => <span className="text-white font-semibold">{children}</span>
                  }}
                >
                  {results.final_report?.decision_framework}
                </ReactMarkdown>
              </div>
            </div>

            {/* Offer Specific Recommendations Loop */}
            <div className="bg-slate-800/30 p-8 rounded-xl border border-slate-700/50">
              <h4 className="text-xl font-bold text-white mb-6">💡 Offer-Specific Recommendations</h4>
              <div className="grid gap-6">
                {results.final_report?.offer_rankings?.map((offer) => (
                  <div key={offer.offer_id} className="bg-slate-900/50 p-6 rounded-lg border border-slate-700">
                    <h5 className="text-lg font-bold text-cyan-300 mb-2">{offer.company} (Rank #{offer.rank})</h5>
                    <div className="text-slate-300 prose prose-invert">
                      <ReactMarkdown>{offer.ai_recommendation || ''}</ReactMarkdown>
                    </div>
                  </div>
                ))}
              </div>
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
                        max: 10,
                        ticks: { display: false, backdropColor: 'transparent' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                        pointLabels: { color: '#94a3b8', font: { size: 12 } }
                      }
                    },
                    plugins: {
                      legend: {
                        position: 'bottom',
                        labels: { color: '#e2e8f0', padding: 20, usePointStyle: true }
                      }
                    }
                  }}
                />
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
