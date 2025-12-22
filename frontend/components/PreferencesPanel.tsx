'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { XMarkIcon, AdjustmentsHorizontalIcon } from '@heroicons/react/24/outline'
import { UserPreferences } from '@/types'
import Slider from './Slider'

interface PreferencesPanelProps {
  preferences: UserPreferences
  onSave: (preferences: UserPreferences) => void
  onClose: () => void
}

const PREFERENCE_DEFINITIONS = [
  {
    key: 'salary_weight' as keyof UserPreferences,
    label: 'Base Salary',
    description: 'Weight of base salary in your decision',
    color: 'green' as const,
    icon: '💰'
  },
  {
    key: 'equity_weight' as keyof UserPreferences,
    label: 'Equity/Stock',
    description: 'Weight of equity value and potential',
    color: 'purple' as const,
    icon: '📈'
  },
  {
    key: 'wlb_weight' as keyof UserPreferences,
    label: 'Work-Life Balance',
    description: 'Weight of work-life balance quality',
    color: 'blue' as const,
    icon: '⚖️'
  },
  {
    key: 'growth_weight' as keyof UserPreferences,
    label: 'Growth Opportunity',
    description: 'Weight of career advancement potential',
    color: 'green' as const,
    icon: '🚀'
  },
  {
    key: 'culture_weight' as keyof UserPreferences,
    label: 'Company Culture',
    description: 'Weight of company culture and values',
    color: 'purple' as const,
    icon: '🏢'
  },
  {
    key: 'benefits_weight' as keyof UserPreferences,
    label: 'Benefits Package',
    description: 'Weight of health, PTO, and other benefits',
    color: 'blue' as const,
    icon: '🎁'
  }
]

const PRESET_PROFILES = [
  {
    name: 'Money Focused',
    description: 'Prioritizes compensation above all',
    icon: '💸',
    weights: {
      salary_weight: 0.50,
      equity_weight: 0.30,
      wlb_weight: 0.05,
      growth_weight: 0.10,
      culture_weight: 0.03,
      benefits_weight: 0.02
    }
  },
  {
    name: 'Growth Focused',
    description: 'Prioritizes learning and advancement',
    icon: '📚',
    weights: {
      salary_weight: 0.20,
      equity_weight: 0.15,
      wlb_weight: 0.15,
      growth_weight: 0.35,
      culture_weight: 0.10,
      benefits_weight: 0.05
    }
  },
  {
    name: 'Life Balance',
    description: 'Prioritizes work-life balance and wellness',
    icon: '🧘',
    weights: {
      salary_weight: 0.20,
      equity_weight: 0.10,
      wlb_weight: 0.40,
      growth_weight: 0.15,
      culture_weight: 0.10,
      benefits_weight: 0.05
    }
  },
  {
    name: 'Balanced',
    description: 'Equally weighted approach',
    icon: '⚖️',
    weights: {
      salary_weight: 0.30,
      equity_weight: 0.20,
      wlb_weight: 0.20,
      growth_weight: 0.15,
      culture_weight: 0.10,
      benefits_weight: 0.05
    }
  }
]



export default function PreferencesPanel({ preferences, onSave, onClose }: PreferencesPanelProps) {
  const [localPreferences, setLocalPreferences] = useState<UserPreferences>(preferences)
  const [activeTab, setActiveTab] = useState<'quick' | 'custom'>('quick')

  // Normalize weights to ensure they sum to 1.0
  const normalizeWeights = (weights: UserPreferences): UserPreferences => {
    const total = Object.values(weights).reduce((sum, value) => sum + value, 0)
    if (total === 0) return weights

    return Object.keys(weights).reduce((normalized, key) => {
      normalized[key as keyof UserPreferences] = weights[key as keyof UserPreferences] / total
      return normalized
    }, {} as UserPreferences)
  }

  // Auto-normalization removed to prevent slider check fighting
  // useEffect(() => {
  //   setLocalPreferences(normalizeWeights(localPreferences))
  // }, [localPreferences])

  const handleWeightChange = (key: keyof UserPreferences, value: number) => {
    // Direct update without immediate normalization
    setLocalPreferences(prev => ({
      ...prev,
      [key]: value / 100
    }))
  }

  const handlePresetSelect = (preset: typeof PRESET_PROFILES[0]) => {
    setLocalPreferences(preset.weights)
  }

  const handleSave = () => {
    try {
      const normalized = normalizeWeights(localPreferences)
      // Standard order - update then close
      onSave(normalized)
      onClose()
    } catch (e) {
      console.error('PreferencesPanel: Error in handleSave:', e)
      onClose()
    }
  }

  const totalWeight = Object.values(localPreferences).reduce((sum, value) => sum + value, 0)

  return (
    <motion.div
      initial={{ opacity: 0, pointerEvents: "none" }}
      animate={{ opacity: 1, pointerEvents: "auto" }}
      exit={{ opacity: 0, pointerEvents: "none" }}
      className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose()
      }}
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="glass-card w-full max-w-4xl max-h-[90vh] flex flex-col rounded-2xl border border-white/10 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex-none flex items-center justify-between p-6 border-b border-white/10 bg-white/5">
          <h3 className="text-xl font-bold text-white flex items-center gap-3">
            <span className="p-2 rounded-lg bg-gradient-to-br from-purple-600 to-pink-600">
              <AdjustmentsHorizontalIcon className="h-5 w-5 text-white" />
            </span>
            Your Preferences
          </h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors text-slate-400 hover:text-white"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex-none flex border-b border-white/10 bg-white/5">
          <button
            onClick={() => setActiveTab('quick')}
            className={`flex-1 py-4 px-4 text-sm font-semibold transition-all relative ${activeTab === 'quick'
              ? 'text-purple-400 bg-white/5'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
          >
            Quick Presets
            {activeTab === 'quick' && (
              <motion.div
                layoutId="activeTabPrefs"
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-purple-400 to-pink-500"
              />
            )}
          </button>
          <button
            onClick={() => setActiveTab('custom')}
            className={`flex-1 py-4 px-4 text-sm font-semibold transition-all relative ${activeTab === 'custom'
              ? 'text-purple-400 bg-white/5'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
          >
            Custom Weights
            {activeTab === 'custom' && (
              <motion.div
                layoutId="activeTabPrefs"
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-purple-400 to-pink-500"
              />
            )}
          </button>
        </div>

        <div className="flex-1 overflow-y-auto min-h-0 p-8 custom-scrollbar">
          {activeTab === 'quick' ? (
            <div className="space-y-6">
              <div>
                <h4 className="text-lg font-semibold text-white mb-2">Choose Your Focus</h4>
                <p className="text-sm text-slate-400 mb-6">
                  Select a preset that matches your career priorities. You can always customize further.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {PRESET_PROFILES.map((preset) => {
                  const isSelected = Object.keys(preset.weights).every(
                    (key) => Math.abs(preset.weights[key as keyof UserPreferences] - localPreferences[key as keyof UserPreferences]) < 0.001
                  )

                  return (
                    <motion.button
                      key={preset.name}
                      onClick={() => handlePresetSelect(preset)}
                      className={`text-left p-6 border rounded-2xl transition-all group relative overflow-hidden ${isSelected
                        ? 'border-purple-500 bg-purple-500/10 shadow-lg shadow-purple-500/20'
                        : 'border-white/10 bg-white/5 hover:border-purple-500/50 hover:bg-white/10'
                        }`}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <div className={`absolute inset-0 bg-gradient-to-br from-purple-500/5 to-pink-500/5 transition-opacity ${isSelected ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
                        }`} />

                      <div className="flex items-center space-x-3 mb-3 relative z-10">
                        <span className="text-2xl">{preset.icon}</span>
                        <h5 className={`text-lg font-bold transition-colors ${isSelected ? 'text-purple-300' : 'text-white group-hover:text-purple-300'
                          }`}>{preset.name}</h5>
                        {isSelected && (
                          <motion.div
                            layoutId="check"
                            className="ml-auto bg-purple-500 rounded-full p-1"
                          >
                            <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                            </svg>
                          </motion.div>
                        )}
                      </div>
                      <p className={`text-sm mb-4 relative z-10 ${isSelected ? 'text-slate-300' : 'text-slate-400'
                        }`}>{preset.description}</p>

                      <div className="space-y-2 relative z-10">
                        {PREFERENCE_DEFINITIONS.map((pref) => (
                          <div key={pref.key} className="flex items-center justify-between">
                            <span className={`text-xs ${isSelected ? 'text-slate-400' : 'text-slate-500'
                              }`}>{pref.label}</span>
                            <span className={`text-xs font-medium ${isSelected ? 'text-purple-200' : 'text-slate-300'
                              }`}>
                              {Math.round(preset.weights[pref.key] * 100)}%
                            </span>
                          </div>
                        ))}
                      </div>
                    </motion.button>
                  )
                })}
              </div>
            </div>
          ) : (
            <div className="space-y-8">
              <div>
                <h4 className="text-lg font-semibold text-white mb-2">Custom Weight Assignment</h4>
                <p className="text-sm text-slate-400 mb-4">
                  Adjust the importance of each factor in your decision-making process.
                </p>

                {totalWeight !== 1.0 && (
                  <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-xl mb-4">
                    <p className="text-sm text-yellow-300 flex items-center gap-2">
                      ⚠️ Weights will be automatically normalized to sum to 100%
                    </p>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 gap-4">
                {PREFERENCE_DEFINITIONS.map((pref) => (
                  <div key={pref.key} className="bg-white/5 p-5 rounded-2xl border border-white/10 hover:border-white/20 transition-colors">
                    <div className="flex items-center gap-4 mb-4">
                      <span className="text-2xl p-2 bg-black/20 rounded-lg">{pref.icon}</span>
                      <div>
                        <h5 className="font-bold text-white">{pref.label}</h5>
                        <p className="text-xs text-slate-400">{pref.description}</p>
                      </div>
                      <div className="ml-auto text-xl font-bold text-purple-400">
                        {Math.round(localPreferences[pref.key] * 100)}%
                      </div>
                    </div>

                    <Slider
                      label=""
                      value={Math.round(localPreferences[pref.key] * 100)}
                      onChange={(value) => handleWeightChange(pref.key, value)}
                      min={0}
                      max={100}
                      color={pref.color}
                    />
                  </div>
                ))}
              </div>

              {/* Weight Summary */}
              <div className="bg-gradient-to-br from-blue-900/40 to-purple-900/40 p-6 rounded-2xl border border-white/10">
                <h5 className="font-bold text-white mb-4">Weight Distribution Summary</h5>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                  {PREFERENCE_DEFINITIONS.map((pref) => (
                    <div key={pref.key} className="flex items-center justify-between p-2 bg-black/20 rounded-lg">
                      <span className="text-slate-300">{pref.label}</span>
                      <span className="font-bold text-white">
                        {Math.round(localPreferences[pref.key] * 100)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex-none flex justify-end space-x-4 p-6 border-t border-white/10 bg-white/5">
          <button
            onClick={onClose}
            className="px-6 py-3 text-slate-300 hover:text-white hover:bg-white/5 rounded-xl transition-colors font-medium"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-8 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white rounded-xl font-bold shadow-lg shadow-purple-500/30 transition-all transform hover:scale-105"
          >
            Save Preferences
          </button>
        </div>
      </motion.div>
    </motion.div>
  )
}
