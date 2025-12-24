'use client'

import { motion } from 'framer-motion'
import {
  BuildingOfficeIcon,
  MapPinIcon,
  TrashIcon,
  CheckCircleIcon,
  PencilSquareIcon
} from '@heroicons/react/24/outline'
import { Offer } from '@/types'

interface OfferCardsProps {
  offers: Offer[]
  selectedOffers: string[]
  onToggleSelection: (offerId: string) => void
  onRemoveOffer: (offerId: string) => void
  onEditOffer: (offer: Offer) => void
}

export default function OfferCards({
  offers,
  selectedOffers,
  onToggleSelection,
  onRemoveOffer,
  onEditOffer
}: OfferCardsProps) {
  const getWorkTypeColor = (workType: string) => {
    switch (workType) {
      case 'remote': return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
      case 'onsite': return 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
      case 'hybrid': return 'bg-purple-500/10 text-purple-400 border border-purple-500/20'
      default: return 'bg-slate-500/10 text-slate-400 border border-slate-500/20'
    }
  }

  const getBenefitsGradeColor = (grade: string) => {
    switch (grade) {
      case 'A+': return 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
      case 'A': return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
      case 'B+': return 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
      case 'B': return 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
      case 'C+': return 'bg-orange-500/10 text-orange-400 border border-orange-500/20'
      case 'C': return 'bg-red-500/10 text-red-400 border border-red-500/20'
      default: return 'bg-slate-500/10 text-slate-400 border border-slate-500/20'
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {offers.map((offer, index) => (
        <motion.div
          key={offer.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className={`relative group rounded-2xl p-6 transition-all duration-300 cursor-pointer overflow-hidden ${selectedOffers.includes(offer.id)
            ? 'bg-blue-600/10 border-blue-500/50 shadow-lg shadow-blue-500/10'
            : 'glass-card hover:-translate-y-1 hover:shadow-cyan-900/20'
            }`}
          onClick={() => onToggleSelection(offer.id)}
        >
          {/* Background Gradient Effect on Hover */}
          <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

          {/* Selection Indicator */}
          {selectedOffers.includes(offer.id) && (
            <div className="absolute top-4 right-4 text-blue-400 animate-fade-in z-20">
              <CheckCircleIcon className="h-6 w-6" />
            </div>
          )}

          {/* Action Buttons Container */}
          <div
            className="absolute top-4 flex items-center space-x-2 z-30 transition-all duration-300"
            style={{ right: selectedOffers.includes(offer.id) ? '4.5rem' : '1rem' }}
          >
            {/* Remove Button */}
            <button
              onClick={(e) => {
                e.stopPropagation()
                onRemoveOffer(offer.id)
              }}
              className="p-2 rounded-full text-slate-500 hover:text-red-400 hover:bg-white/10 transition-all opacity-0 group-hover:opacity-100"
              title="Remove Offer"
            >
              <TrashIcon className="h-5 w-5" />
            </button>

            {/* Edit Button */}
            <button
              onClick={(e) => {
                e.stopPropagation()
                onEditOffer(offer)
              }}
              className="p-2 rounded-full text-slate-500 hover:text-cyan-400 hover:bg-white/10 transition-all opacity-0 group-hover:opacity-100"
              title="Edit Offer"
            >
              <PencilSquareIcon className="h-5 w-5" />
            </button>
          </div>

          {/* Company Header */}
          <div className="flex items-start space-x-4 mb-6">
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 p-3 rounded-xl border border-white/5 shadow-inner">
              <BuildingOfficeIcon className="h-6 w-6 text-cyan-400" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-bold text-white truncate group-hover:text-cyan-200 transition-colors">{offer.company}</h3>
              <p className="text-sm text-slate-400 truncate">{offer.position}</p>
            </div>
          </div>

          {/* Location & Work Type */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center text-sm text-slate-400">
              <MapPinIcon className="h-4 w-4 mr-1.5" />
              <span className="truncate max-w-[120px]" title={offer.location}>{offer.location}</span>
            </div>
            <span className={`px-2.5 py-1 text-xs font-semibold rounded-full uppercase tracking-wide ${getWorkTypeColor(offer.work_type)}`}>
              {offer.work_type}
            </span>
          </div>

          {/* Compensation */}
          <div className="space-y-3 mb-6 bg-black/20 p-4 rounded-xl border border-white/5">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">Base Salary</span>
              <span className="font-semibold text-white tracking-wide">
                ${offer.base_salary.toLocaleString()}
              </span>
            </div>

            {offer.equity > 0 && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Equity</span>
                <span className="font-medium text-slate-300">
                  ${offer.equity.toLocaleString()}
                </span>
              </div>
            )}

            {((offer.bonus || 0) > 0 || (offer.signing_bonus || 0) > 0) && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Bonuses</span>
                <span className="font-medium text-slate-300">
                  ${((offer.bonus || 0) + (offer.signing_bonus || 0)).toLocaleString()}
                </span>
              </div>
            )}

            <div className="flex items-center justify-between pt-3 border-t border-white/10 mt-2">
              <span className="text-sm font-medium text-white/70">Total Comp</span>
              <span className="font-bold text-lg text-gradient">
                ${(offer.total_compensation || (offer.base_salary || 0) + (offer.equity || 0) + (offer.bonus || 0)).toLocaleString()}
              </span>
            </div>
          </div>

          {/* Ratings */}
          <div className="grid grid-cols-3 gap-2 mb-4">
            <div className="p-2 rounded-lg bg-white/5 text-center border border-white/5">
              <div className="text-sm font-bold text-white">{offer.wlb_score}/10</div>
              <div className="text-[10px] uppercase tracking-wider text-slate-500 mt-1">WLB</div>
            </div>
            <div className="p-2 rounded-lg bg-white/5 text-center border border-white/5">
              <div className="text-sm font-bold text-white">{offer.growth_score}/10</div>
              <div className="text-[10px] uppercase tracking-wider text-slate-500 mt-1">Growth</div>
            </div>
            <div className="p-2 rounded-lg bg-white/5 text-center border border-white/5">
              <div className="text-sm font-bold text-white">{offer.role_fit}/10</div>
              <div className="text-[10px] uppercase tracking-wider text-slate-500 mt-1">Fit</div>
            </div>
          </div>

          {/* Benefits Grade */}
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium uppercase tracking-wider text-slate-500">Benefits</span>
            <span className={`px-3 py-0.5 text-xs font-bold rounded-full ${getBenefitsGradeColor(offer.benefits_grade)}`}>
              Grade {offer.benefits_grade}
            </span>
          </div>

          {/* Analysis Results (if available) */}
          {offer.total_score && (
            <div className="mt-4 pt-4 border-t border-white/10">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-slate-300">AI Score</span>
                <div className="flex items-center space-x-3">
                  <div className="w-20 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-cyan-400 to-blue-500"
                      style={{ width: `${(offer.total_score / 10) * 100}%` }}
                    />
                  </div>
                  <span className="text-lg font-bold text-cyan-400">
                    {offer.total_score.toFixed(1)}
                  </span>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      ))}
    </div>
  )
}
