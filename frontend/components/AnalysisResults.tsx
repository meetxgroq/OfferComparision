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
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import { Radar, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  RadialLinearScale,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
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
  Tooltip,
  Legend
)

interface AnalysisResultsProps {
  results: AnalysisResults
}

export default function AnalysisResults({ results }: AnalysisResultsProps) {
  const [activeTab, setActiveTab] = useState<'ai' | 'charts' | 'table' | 'timeline'>('ai')
  const [expandedNegotiationOptions, setExpandedNegotiationOptions] = useState<Set<string>>(new Set())

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
            {/* The smart choice - Enhanced Slogan Section */}
            {(() => {
              const verdict = results.final_report?.verdict;
              const topOffer = results.comparison_results?.top_offer;
              const netValueAnalysis = results.final_report?.net_value_analysis;
              
              // Determine conclusion
              let conclusion = "Analysis Complete";
              let explanation = "Review the detailed analysis below.";
              let icon = "✨";
              
              if (verdict?.recommended_company) {
                const winner = netValueAnalysis?.offers?.find(
                  (o: any) => o.offer_id === netValueAnalysis.winner
                );
                const discretionaryIncome = winner?.discretionary_income || 0;
                const delta = winner?.discretionary_income_delta || 0;
                
                if (delta > 10000) {
                  conclusion = `${verdict.recommended_company} Wins`;
                  explanation = `Financially superior with $${delta.toLocaleString()} more in discretionary income annually.`;
                  icon = "🏆";
                } else if (delta > 0) {
                  conclusion = `${verdict.recommended_company} Leads`;
                  explanation = `Slightly ahead with $${delta.toLocaleString()} more in discretionary income.`;
                  icon = "📈";
                } else if (Math.abs(delta) < 5000) {
                  conclusion = "It's a Toss-Up";
                  explanation = "Both offers are financially similar. Consider non-financial factors.";
                  icon = "⚖️";
                } else {
                  conclusion = `${verdict.recommended_company} Recommended`;
                  explanation = verdict.reasoning?.[0] || "Based on comprehensive analysis.";
                  icon = "✅";
                }
              } else if (topOffer?.company) {
                conclusion = `${topOffer.company} is Top Choice`;
                explanation = `Highest overall score of ${topOffer.total_score?.toFixed(1) || 'N/A'}/100.`;
                icon = "⭐";
              }
              
              return (
                <motion.div
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5 }}
                  className="relative bg-gradient-to-br from-purple-600/30 via-blue-600/30 to-cyan-600/30 border-2 border-purple-500/40 rounded-2xl p-8 mb-8 shadow-2xl overflow-hidden"
                >
                  {/* Decorative background elements */}
                  <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-cyan-500/10 to-purple-500/10 rounded-full blur-3xl -mr-32 -mt-32"></div>
                  <div className="absolute bottom-0 left-0 w-48 h-48 bg-gradient-to-tr from-blue-500/10 to-purple-500/10 rounded-full blur-2xl -ml-24 -mb-24"></div>
                  
                  <div className="relative z-10">
                    <div className="flex items-center gap-3 mb-4">
                      <span className="text-4xl">{icon}</span>
                      <p className="text-purple-200 text-sm font-bold tracking-widest uppercase">The smart choice</p>
                    </div>
                    <h2 className="text-6xl font-extrabold text-white mb-5 leading-tight bg-gradient-to-r from-white via-cyan-100 to-blue-200 bg-clip-text text-transparent">
                      {conclusion}
                    </h2>
                    <p className="text-slate-100 text-xl leading-relaxed font-medium max-w-3xl">{explanation}</p>
                  </div>
                </motion.div>
              );
            })()}

            {/* Executive Summary - Styled Distinctly */}
            <div className="bg-gradient-to-br from-indigo-900/40 to-slate-900 p-8 rounded-xl border border-indigo-500/30 shadow-lg">
              <div className="flex items-center space-x-3 mb-6">
                <div className="bg-indigo-600/20 p-2 rounded-lg border border-indigo-500/50">
                  <SparklesIcon className="h-6 w-6 text-indigo-400" />
                </div>
                <h4 className="text-xl font-bold text-indigo-100">Executive Summary</h4>
              </div>
              
              {/* Score Visualization Section */}
              {rankedOffers.length > 0 && (() => {
                const scores = rankedOffers.map(o => o.total_score || 0).filter(s => s > 0);
                const minScore = scores.length > 0 ? Math.min(...scores) : 0;
                const maxScore = scores.length > 0 ? Math.max(...scores) : 0;
                const avgScore = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
                const topOffer = rankedOffers[0];
                
                return (
                  <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Score Comparison Bars */}
                    <div className="space-y-4">
                      <h5 className="text-sm font-semibold text-indigo-300 uppercase tracking-wide">Score Comparison</h5>
                      <div className="space-y-3">
                        {rankedOffers.map((offer, idx) => {
                          const score = offer.total_score || 0;
                          const isTop = idx === 0;
                          return (
                            <div key={offer.offer_id || idx} className="space-y-1.5">
                              <div className="flex items-center justify-between text-sm">
                                <div className="flex items-center gap-2">
                                  <span className="text-slate-300 font-medium">{offer.company}</span>
                                  {isTop && (
                                    <span className="px-2 py-0.5 bg-green-600/20 text-green-400 text-xs font-semibold rounded border border-green-500/50">
                                      Top
                                    </span>
                                  )}
                                </div>
                                <span className={`font-bold ${isTop ? 'text-green-400' : 'text-slate-400'}`}>
                                  {score.toFixed(1)}/100
                                </span>
                              </div>
                              <div className="w-full bg-slate-700/50 rounded-full h-3 shadow-inner">
                                <motion.div
                                  initial={{ width: 0 }}
                                  animate={{ width: `${score}%` }}
                                  transition={{ duration: 0.8, delay: idx * 0.1, ease: "easeOut" }}
                                  className={`h-3 rounded-full ${
                                    isTop 
                                      ? 'bg-gradient-to-r from-green-500 to-emerald-400 shadow-sm shadow-green-500/30' 
                                      : 'bg-gradient-to-r from-slate-500 to-slate-400'
                                  }`}
                                />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                    
                    {/* Score Statistics */}
                    <div className="space-y-4">
                      <h5 className="text-sm font-semibold text-indigo-300 uppercase tracking-wide">Score Statistics</h5>
                      <div className="space-y-3">
                        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-slate-400 text-sm">Top Score</span>
                            <span className="text-green-400 font-bold text-lg">{maxScore.toFixed(1)}</span>
                          </div>
                          <div className="text-xs text-slate-500">{topOffer?.company || 'N/A'}</div>
                        </div>
                        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-slate-400 text-sm">Average Score</span>
                            <span className="text-indigo-400 font-bold text-lg">{avgScore.toFixed(1)}</span>
                          </div>
                          <div className="text-xs text-slate-500">Across all offers</div>
                        </div>
                        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-slate-400 text-sm">Score Range</span>
                            <span className="text-slate-300 font-semibold">{minScore.toFixed(1)} - {maxScore.toFixed(1)}</span>
                          </div>
                          <div className="text-xs text-slate-500">Gap: {(maxScore - minScore).toFixed(1)} points</div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })()}
              
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

            {/* Net Value Analysis Section */}
            {results.final_report?.net_value_analysis && (
              <div className="bg-gradient-to-br from-green-900/30 to-slate-900 p-8 rounded-xl border border-green-500/30 shadow-lg">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="bg-green-600/20 p-2 rounded-lg border border-green-500/50">
                    <span className="text-2xl">💰</span>
                  </div>
                  <h4 className="text-xl font-bold text-green-100">Net Value Analysis</h4>
                </div>
                
                {/* Summary Table */}
                {results.final_report?.summary_table?.headers && results.final_report?.summary_table?.rows && (
                  <div className="mb-6 overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="bg-slate-800/50 border-b border-slate-700">
                          {results.final_report.summary_table.headers.map((header: string, idx: number) => (
                            <th key={idx} className={`p-4 font-semibold ${idx === 0 ? 'text-slate-300' : 'text-white'}`}>
                              {header}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-700">
                        {results.final_report.summary_table.rows.map((row: string[], rowIdx: number) => {
                          const isLastRow = rowIdx === results.final_report.summary_table.rows.length - 1;
                          const winnerOfferId = results.final_report?.net_value_analysis?.winner;
                          
                          // Find the winner's company name to match with table headers
                          const winnerOffer = results.final_report?.net_value_analysis?.offers?.find(
                            (o: any) => o.offer_id === winnerOfferId
                          );
                          const winnerCompany = winnerOffer?.company;
                          
                          // Get headers to match column index with company name
                          const headers = results.final_report.summary_table.headers || [];
                          
                          // Extract numeric values for visualization (skip first column which is the label)
                          const numericValues = row.slice(1).map((cell: string) => {
                            // Remove currency symbols, commas, and extract number
                            const numStr = cell.replace(/[$,]/g, '').trim();
                            const num = parseFloat(numStr);
                            return isNaN(num) ? 0 : num;
                          });
                          const maxValue = Math.max(...numericValues, 1); // Avoid division by zero
                          
                          return (
                            <>
                              <tr key={rowIdx} className="hover:bg-slate-800/30 transition-colors">
                                {row.map((cell: string, cellIdx: number) => {
                                  const isDiscretionaryIncome = cell.includes('Discretionary Income');
                                  // Only show winner tag if:
                                  // 1. It's the last row (Final Discretionary Income)
                                  // 2. It's not the first column (metric label)
                                  // 3. The current column's header matches the winner's company
                                  const isWinner = isLastRow && 
                                                  cellIdx > 0 && 
                                                  winnerCompany && 
                                                  headers[cellIdx] === winnerCompany;
                                  
                                  return (
                                    <td
                                      key={cellIdx}
                                      className={`p-4 ${
                                        cellIdx === 0
                                          ? 'text-slate-300 font-medium'
                                          : isLastRow && isDiscretionaryIncome
                                          ? 'text-green-400 font-bold text-lg'
                                          : 'text-slate-200'
                                      }`}
                                    >
                                      {cell}
                                      {isWinner && (
                                        <span className="ml-2 px-2 py-1 bg-green-600/20 text-green-400 text-xs font-semibold rounded border border-green-500/50">
                                          Winner
                                        </span>
                                      )}
                                    </td>
                                  );
                                })}
                              </tr>
                              {/* Visualization row for each metric */}
                              {numericValues.length > 0 && (
                                <tr key={`viz-${rowIdx}`} className="bg-slate-900/30">
                                  <td className="p-2"></td>
                                  {numericValues.map((value: number, valIdx: number) => {
                                    const header = headers[valIdx + 1];
                                    const isWinnerCol = winnerCompany && header === winnerCompany;
                                    const percentage = (value / maxValue) * 100;
                                    
                                    return (
                                      <td key={valIdx} className="p-2">
                                        <div className="relative">
                                          <div className="w-full bg-slate-700/50 rounded-full h-2.5 mb-1">
                                            <motion.div
                                              initial={{ width: 0 }}
                                              animate={{ width: `${percentage}%` }}
                                              transition={{ duration: 0.6, delay: rowIdx * 0.1 }}
                                              className={`h-2.5 rounded-full ${
                                                isWinnerCol && isLastRow
                                                  ? 'bg-gradient-to-r from-green-500 to-emerald-400'
                                                  : 'bg-gradient-to-r from-slate-500 to-slate-400'
                                              }`}
                                            />
                                          </div>
                                          <div className="text-xs text-slate-400 text-center">
                                            {percentage.toFixed(0)}%
                                          </div>
                                        </div>
                                      </td>
                                    );
                                  })}
                                </tr>
                              )}
                            </>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* Discretionary Income Highlight */}
                {results.final_report?.net_value_analysis?.winner && (
                  <div className="bg-green-600/10 border border-green-500/30 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-green-300 text-sm font-medium">Financial Winner</p>
                        <p className="text-green-100 text-2xl font-bold mt-1">
                          {(() => {
                            const winnerId = results.final_report.net_value_analysis.winner;
                            const winnerOffer = results.final_report.net_value_analysis.offers?.find(
                              (o: any) => o.offer_id === winnerId
                            );
                            return winnerOffer?.company || 'Unknown';
                          })()}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-green-300 text-sm font-medium">Discretionary Income</p>
                        <p className="text-green-100 text-3xl font-bold mt-1">
                          ${results.final_report.net_value_analysis.winner_discretionary_income?.toLocaleString() || '0'}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* How Your Offer Compares - Percentile Visualization */}
            {rankedOffers.length > 0 && (
              <div className="bg-slate-800/30 p-8 rounded-xl border border-slate-700/50">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="bg-blue-600/20 p-2 rounded-lg border border-blue-500/50">
                    <ChartBarIcon className="h-6 w-6 text-blue-400" />
                  </div>
                  <div>
                    <h4 className="text-xl font-bold text-white">How Your Offer Compares</h4>
                    <p className="text-slate-400 text-sm mt-1">Benchmarked against market data</p>
                  </div>
                </div>
                
                <div className="space-y-8">
                  {rankedOffers.map((offer, offerIdx) => {
                    const marketAnalysis = offer.offer_data?.market_analysis || {};
                    const totalCompAnalysis = offer.offer_data?.total_comp_analysis || {};
                    const basePercentile = marketAnalysis.market_percentile || 50;
                    const totalPercentile = totalCompAnalysis.market_percentile || 50;
                    const baseSalary = offer.offer_data?.base_salary || 0;
                    const totalComp = offer.offer_data?.total_compensation || 0;
                    const medianBase = marketAnalysis.market_range?.median || 0;
                    const medianTotal = totalCompAnalysis.market_range?.median || 0;
                    
                    const getPercentileColor = (percentile: number) => {
                      if (percentile < 25) return { bg: 'bg-red-500', text: 'text-red-400' };
                      if (percentile < 50) return { bg: 'bg-orange-500', text: 'text-orange-400' };
                      if (percentile < 75) return { bg: 'bg-yellow-500', text: 'text-yellow-400' };
                      return { bg: 'bg-green-500', text: 'text-green-400' };
                    };
                    
                    const baseColor = getPercentileColor(basePercentile);
                    const totalColor = getPercentileColor(totalPercentile);
                    
                    const getOrdinalSuffix = (n: number) => {
                      const s = ['th', 'st', 'nd', 'rd'];
                      const v = n % 100;
                      return n + (s[(v - 20) % 10] || s[v] || s[0]);
                    };
                    
                    return (
                      <div key={offer.offer_id || offerIdx} className="bg-slate-900/50 border border-slate-700 rounded-lg p-6">
                        <h5 className="text-lg font-semibold text-white mb-6">{offer.company} - {offer.offer_data?.position || 'Position'}</h5>
                        
                        {/* Base Salary Percentile */}
                        <div className="mb-6">
                          <div className="flex items-center justify-between mb-2.5">
                            <span className="text-slate-300 text-sm font-medium">Base Salary</span>
                            <span className={`${baseColor.text} font-semibold text-sm`}>
                              {getOrdinalSuffix(Math.round(basePercentile))} percentile
                            </span>
                          </div>
                          <div className="w-full bg-slate-700/50 rounded-full h-3 mb-2.5 shadow-inner">
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${Math.min(100, Math.max(0, basePercentile))}%` }}
                              transition={{ duration: 0.8, ease: "easeOut" }}
                              className={`${baseColor.bg} h-3 rounded-full transition-all duration-500 shadow-sm`}
                              style={{ boxShadow: `0 0 8px ${baseColor.bg.replace('bg-', '').split('-')[0] === 'red' ? 'rgba(239, 68, 68, 0.4)' : baseColor.bg.replace('bg-', '').split('-')[0] === 'orange' ? 'rgba(249, 115, 22, 0.4)' : baseColor.bg.replace('bg-', '').split('-')[0] === 'yellow' ? 'rgba(234, 179, 8, 0.4)' : 'rgba(34, 197, 94, 0.4)'}` }}
                            />
                          </div>
                          <div className="flex items-center justify-between text-xs text-slate-400">
                            <span>Your Offer: <span className="text-slate-300 font-medium">${baseSalary.toLocaleString()}</span></span>
                            {medianBase > 0 && (
                              <span>Median: <span className="text-slate-300 font-medium">${medianBase.toLocaleString()}</span></span>
                            )}
                          </div>
                        </div>
                        
                        {/* Total Compensation Percentile */}
                        <div>
                          <div className="flex items-center justify-between mb-2.5">
                            <span className="text-slate-300 text-sm font-medium">Total Compensation</span>
                            <span className={`${totalColor.text} font-semibold text-sm`}>
                              {getOrdinalSuffix(Math.round(totalPercentile))} percentile
                            </span>
                          </div>
                          <div className="w-full bg-slate-700/50 rounded-full h-3 mb-2.5 shadow-inner">
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${Math.min(100, Math.max(0, totalPercentile))}%` }}
                              transition={{ duration: 0.8, ease: "easeOut", delay: 0.1 }}
                              className={`${totalColor.bg} h-3 rounded-full transition-all duration-500 shadow-sm`}
                              style={{ boxShadow: `0 0 8px ${totalColor.bg.replace('bg-', '').split('-')[0] === 'red' ? 'rgba(239, 68, 68, 0.4)' : totalColor.bg.replace('bg-', '').split('-')[0] === 'orange' ? 'rgba(249, 115, 22, 0.4)' : totalColor.bg.replace('bg-', '').split('-')[0] === 'yellow' ? 'rgba(234, 179, 8, 0.4)' : 'rgba(34, 197, 94, 0.4)'}` }}
                            />
                          </div>
                          <div className="flex items-center justify-between text-xs text-slate-400">
                            <span>Your Offer: <span className="text-slate-300 font-medium">${totalComp.toLocaleString()}</span></span>
                            {medianTotal > 0 && (
                              <span>Median: <span className="text-slate-300 font-medium">${medianTotal.toLocaleString()}</span></span>
                            )}
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

            {/* Verdict & Recommendation Section (replaces Comprehensive Analysis) */}
            {results.final_report?.verdict && (
              <div className="bg-slate-800/30 p-8 rounded-xl border border-slate-700/50">
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

            {/* Reality Checks Section */}
            {results.final_report?.reality_checks && (
              <div className="bg-gradient-to-br from-red-900/20 to-orange-900/20 p-8 rounded-xl border border-red-500/30 shadow-lg">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="bg-red-600/20 p-2 rounded-lg border border-red-500/50">
                    <ExclamationTriangleIcon className="h-6 w-6 text-red-400" />
                  </div>
                  <h4 className="text-xl font-bold text-red-100">Reality Checks</h4>
                </div>
                
                {/* Red Flags */}
                {results.final_report.reality_checks.red_flags && 
                 Array.isArray(results.final_report.reality_checks.red_flags) && 
                 results.final_report.reality_checks.red_flags.length > 0 && (
                  <div className="mb-6">
                    <h5 className="text-lg font-semibold text-red-300 mb-4 flex items-center gap-2">
                      <span className="text-2xl">🚩</span>
                      Red Flags
                    </h5>
                    <div className="space-y-3">
                      {results.final_report.reality_checks.red_flags.map((flag: string, idx: number) => (
                        <div key={idx} className="bg-red-950/30 border border-red-500/30 rounded-lg p-4 flex items-start space-x-3">
                          <ExclamationTriangleIcon className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
                          <p className="text-red-200 flex-1">{flag}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Considerations */}
                {results.final_report.reality_checks.considerations && 
                 Array.isArray(results.final_report.reality_checks.considerations) && 
                 results.final_report.reality_checks.considerations.length > 0 && (
                  <div>
                    <h5 className="text-lg font-semibold text-orange-300 mb-4 flex items-center gap-2">
                      <span className="text-2xl">💡</span>
                      Important Considerations
                    </h5>
                    <div className="space-y-3">
                      {results.final_report.reality_checks.considerations.map((consideration: string, idx: number) => (
                        <div key={idx} className="bg-orange-950/20 border border-orange-500/30 rounded-lg p-4 flex items-start space-x-3">
                          <span className="text-orange-400 text-xl">•</span>
                          <p className="text-orange-200 flex-1">{consideration}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

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

            {/* Negotiation Opportunities Section - Collapsible Options */}
            {(() => {
              const negotiationOptions = results.final_report?.negotiation_options || [];
              const hasOptions = negotiationOptions.length > 0;
              
              // Fallback to simple list if structured options not available
              const simpleOpportunities = results.final_report?.negotiation_opportunities || [];
              const hasSimpleList = !hasOptions && Array.isArray(simpleOpportunities) && simpleOpportunities.length > 0;
              
              if (!hasOptions && !hasSimpleList) return null;
              
              const copyScript = (script: string, e: React.MouseEvent) => {
                e.stopPropagation();
                navigator.clipboard.writeText(script).then(() => {
                  alert('Script copied to clipboard!');
                }).catch(() => {
                  alert('Failed to copy script');
                });
              };
              
              const toggleOption = (optionId: string) => {
                setExpandedNegotiationOptions(prev => {
                  const newSet = new Set(prev);
                  if (newSet.has(optionId)) {
                    newSet.delete(optionId);
                  } else {
                    newSet.add(optionId);
                  }
                  return newSet;
                });
              };
              
              return (
                <div className="bg-gradient-to-br from-amber-900/20 to-slate-900 p-8 rounded-xl border border-amber-500/30 shadow-lg">
                  <div className="flex items-center space-x-3 mb-6">
                    <div className="bg-amber-600/20 p-2 rounded-lg border border-amber-500/50">
                      <span className="text-2xl">💼</span>
                    </div>
                    <h4 className="text-xl font-bold text-amber-100">Negotiation Opportunities</h4>
                  </div>
                  
                  {hasOptions ? (
                    <div className="space-y-3">
                      {negotiationOptions.map((option: any) => {
                        const difficultyColors = {
                          'likely_achievable': { bg: 'bg-green-600/20', text: 'text-green-400', border: 'border-green-500/50' },
                          'worth_asking': { bg: 'bg-orange-600/20', text: 'text-orange-400', border: 'border-orange-500/50' },
                          'ambitious_ask': { bg: 'bg-red-600/20', text: 'text-red-400', border: 'border-red-500/50' }
                        };
                        const colors = difficultyColors[option.difficulty as keyof typeof difficultyColors] || difficultyColors.worth_asking;
                        const isExpanded = expandedNegotiationOptions.has(option.id);
                        
                        return (
                          <div
                            key={option.id}
                            className={`border-2 rounded-lg overflow-hidden transition-all ${
                              isExpanded
                                ? 'border-cyan-500 bg-cyan-900/20 shadow-lg shadow-cyan-500/20'
                                : 'border-slate-700 hover:border-slate-600 bg-slate-800/50'
                            }`}
                          >
                            {/* Header - Clickable */}
                            <div
                              onClick={() => toggleOption(option.id)}
                              className="p-4 cursor-pointer flex items-start justify-between"
                            >
                              <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                  <span className={`px-2 py-1 rounded text-xs font-semibold ${colors.bg} ${colors.text} border ${colors.border}`}>
                                    {option.difficulty_label || option.difficulty}
                                  </span>
                                </div>
                                <h5 className="text-white font-semibold mb-1">{option.title}</h5>
                                <p className="text-slate-400 text-sm">{option.description}</p>
                              </div>
                              <ChevronDownIcon
                                className={`h-5 w-5 text-slate-400 transition-transform duration-300 flex-shrink-0 ml-4 ${
                                  isExpanded ? 'transform rotate-180' : ''
                                }`}
                              />
                            </div>
                            
                            {/* Expandable Content - Script */}
                            <motion.div
                              initial={false}
                              animate={{
                                height: isExpanded ? 'auto' : 0,
                                opacity: isExpanded ? 1 : 0
                              }}
                              transition={{ duration: 0.3, ease: 'easeInOut' }}
                              className="overflow-hidden"
                            >
                              {isExpanded && (
                                <div className="px-4 pb-4 border-t border-slate-700/50 pt-4">
                                  <div className="flex items-center justify-between mb-3">
                                    <h6 className="text-white font-semibold text-sm">Negotiation Script</h6>
                                    <button
                                      onClick={(e) => copyScript(option.script, e)}
                                      className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-medium transition-colors flex items-center gap-2"
                                    >
                                      <DocumentArrowDownIcon className="h-3.5 w-3.5" />
                                      Copy
                                    </button>
                                  </div>
                                  <div className="bg-slate-950 border border-slate-700 rounded-lg p-4 text-slate-300 whitespace-pre-wrap leading-relaxed text-sm">
                                    {option.script}
                                  </div>
                                </div>
                              )}
                            </motion.div>
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
                      { label: 'Base Salary', key: 'base_salary', format: 'currency', color: 'text-red-400', isPositive: true },
                      { label: 'Equity', key: 'equity', format: 'currency', color: 'text-amber-400', isPositive: true },
                      { label: 'Bonus', key: 'bonus', format: 'currency', color: 'text-emerald-400', isPositive: true },
                      { label: 'Total Comp', key: 'total_compensation', format: 'currency', color: 'text-white font-bold', isPositive: true, isKeyMetric: true },
                      {
                        label: 'Estimated Net Pay',
                        key: 'estimated_net_pay',
                        format: 'currency',
                        color: 'text-emerald-300 font-semibold',
                        tooltip: 'Estimated take-home pay after Federal, State, and FICA taxes based on location.',
                        isPositive: true,
                        isKeyMetric: true
                      },
                      {
                        label: 'Estimated Annual Expenses',
                        key: 'estimated_annual_expenses',
                        format: 'currency',
                        color: 'text-red-300',
                        tooltip: 'Estimated basic living expenses for a single person in this location.',
                        isPositive: false
                      },
                      {
                        label: 'Net Savings',
                        key: 'net_savings',
                        format: 'currency',
                        color: 'text-cyan-300 font-bold',
                        tooltip: 'Estimated potential savings (Net Pay - Annual Expenses).',
                        isPositive: true,
                        isKeyMetric: true
                      },
                      { label: 'Job Level', key: 'level', format: 'text', color: 'text-slate-200', isPositive: null },
                      // Add more metrics as needed
                    ].map((row, idx) => {
                      // Extract numeric values for visualization (skip first column which is the label)
                      const numericValues = rankedOffers.map(o => {
                        const val = o.offer_data?.[row.key] || 0;
                        // For text format, return 0 (no visualization)
                        if (row.format === 'text') return 0;
                        return typeof val === 'number' ? val : parseFloat(String(val)) || 0;
                      });
                      const maxValue = Math.max(...numericValues, 1); // Avoid division by zero
                      
                      // Find winner for key metrics
                      let winnerCompany = null;
                      if (row.isKeyMetric && row.isPositive) {
                        const maxIdx = numericValues.indexOf(maxValue);
                        if (maxIdx >= 0 && rankedOffers[maxIdx]) {
                          winnerCompany = rankedOffers[maxIdx].company;
                        }
                      }
                      
                      return (
                        <>
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
                            {rankedOffers.map((o, offerIdx) => {
                              const val = o.offer_data?.[row.key] || 0;
                              const display = row.format === 'currency'
                                ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val)
                                : val;
                              const isWinner = row.isKeyMetric && winnerCompany === o.company;
                              return (
                                <td key={o.offer_id} className={`p-4 ${row.color}`}>
                                  {display}
                                  {isWinner && (
                                    <span className="ml-2 px-2 py-0.5 bg-green-600/20 text-green-400 text-xs font-semibold rounded border border-green-500/50">
                                      Winner
                                    </span>
                                  )}
                                </td>
                              )
                            })}
                          </tr>
                          {/* Visualization row for each metric (skip text format) */}
                          {row.format !== 'text' && numericValues.length > 0 && maxValue > 0 && (
                            <tr key={`viz-${idx}`} className="bg-slate-900/30">
                              <td className="p-2"></td>
                              {numericValues.map((value: number, valIdx: number) => {
                                const offer = rankedOffers[valIdx];
                                const isWinnerCol = row.isKeyMetric && winnerCompany === offer?.company;
                                const percentage = (value / maxValue) * 100;
                                
                                // Determine bar color based on metric type
                                let barColor = 'bg-gradient-to-r from-slate-500 to-slate-400';
                                if (row.isPositive === true) {
                                  barColor = isWinnerCol && row.isKeyMetric
                                    ? 'bg-gradient-to-r from-green-500 to-emerald-400'
                                    : 'bg-gradient-to-r from-blue-500 to-cyan-400';
                                } else if (row.isPositive === false) {
                                  barColor = 'bg-gradient-to-r from-red-500 to-orange-400';
                                }
                                
                                return (
                                  <td key={valIdx} className="p-2">
                                    <div className="relative">
                                      <div className="w-full bg-slate-700/50 rounded-full h-2.5 mb-1 shadow-inner">
                                        <motion.div
                                          initial={{ width: 0 }}
                                          animate={{ width: `${percentage}%` }}
                                          transition={{ duration: 0.6, delay: idx * 0.05, ease: "easeOut" }}
                                          className={`h-2.5 rounded-full ${barColor} shadow-sm`}
                                        />
                                      </div>
                                      <div className="text-xs text-slate-400 text-center">
                                        {percentage.toFixed(0)}%
                                      </div>
                                    </div>
                                  </td>
                                );
                              })}
                            </tr>
                          )}
                        </>
                      );
                    })}
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
