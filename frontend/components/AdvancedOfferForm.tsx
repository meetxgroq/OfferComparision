'use client'

import { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import {
  XMarkIcon,
  DocumentTextIcon,
  CloudArrowUpIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/outline'
import { Offer, WORK_TYPES, EMPLOYMENT_TYPES, DOMAINS, BENEFITS_GRADES } from '@/types'
import { POPULAR_COMPANIES } from '@/data/companies'
import FileUpload from './FileUpload'
import Slider from './Slider'

interface AdvancedOfferFormProps {
  onSubmit: (offer: Offer) => void
  onClose: () => void
  editOffer?: Offer
}

export default function AdvancedOfferForm({ onSubmit, onClose, editOffer }: AdvancedOfferFormProps) {
  const [activeTab, setActiveTab] = useState<'manual' | 'upload'>('manual')
  const [formData, setFormData] = useState<Partial<Offer>>({
    company: editOffer?.company || '',
    position: editOffer?.position || '',
    location: editOffer?.location || '',
    base_salary: editOffer?.base_salary || 0,
    equity: editOffer?.equity || 0,
    bonus: editOffer?.bonus || 0,
    signing_bonus: editOffer?.signing_bonus || 0,
    work_type: editOffer?.work_type || 'hybrid',
    employment_type: editOffer?.employment_type || 'full-time',
    domain: editOffer?.domain || '',
    level: editOffer?.level || '',
    benefits_grade: editOffer?.benefits_grade || 'B',
    wlb_grade: editOffer?.wlb_grade || '',
    wlb_score: editOffer?.wlb_score || 7,
    growth_grade: editOffer?.growth_grade || '',
    growth_score: editOffer?.growth_score || 7,
    // role_fit removed
    job_description: editOffer?.job_description || '',
    relocation_support: editOffer?.relocation_support || false,
    other_perks: editOffer?.other_perks || ''
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isUploading, setIsUploading] = useState(false)
  const [suggestions, setSuggestions] = useState<typeof POPULAR_COMPANIES>([])
  const [showSuggestions, setShowSuggestions] = useState(false)

  const validateForm = useCallback(() => {
    const newErrors: Record<string, string> = {}

    if (!formData.company?.trim()) newErrors.company = 'Company is required'
    if (!formData.position?.trim()) newErrors.position = 'Position is required'
    if (!formData.location?.trim()) newErrors.location = 'Location is required'
    if (!formData.base_salary || formData.base_salary <= 0) newErrors.base_salary = 'Valid base salary is required'

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }, [formData])

  const getScoreFromGrade = (grade: string): number => {
    switch (grade) {
      case 'A+': return 10
      case 'A': return 9
      case 'B+': return 8
      case 'B': return 8
      case 'C+': return 7
      case 'C': return 6
      case 'D': return 4
      case 'F': return 2
      default: return 7
    }
  }

  const handleCompanyChange = (value: string) => {
    handleInputChange('company', value)

    // Auto-suggest logic
    if (value.trim().length > 0) {
      const matches = POPULAR_COMPANIES.filter(c =>
        c.name.toLowerCase().includes(value.toLowerCase())
      )
      setSuggestions(matches)
      setShowSuggestions(true)
    } else {
      setSuggestions([])
      setShowSuggestions(false)
    }

    // Auto-populate logic (Exact match)
    const match = POPULAR_COMPANIES.find(c => c.name.toLowerCase() === value.toLowerCase())
    if (match) {
      setFormData(prev => ({
        ...prev,
        company: match.name,
        benefits_grade: match.benefits_grade,
        wlb_grade: match.wlb_grade,
        wlb_score: getScoreFromGrade(match.wlb_grade),
        growth_grade: match.growth_grade,
        growth_score: getScoreFromGrade(match.growth_grade),
      }))
      if (match.levels) {
        setLevelSuggestions(match.levels)
      }
    } else {
      setLevelSuggestions([])
    }
  }

  const [levelSuggestions, setLevelSuggestions] = useState<string[]>(() => {
    if (editOffer?.company) {
      const match = POPULAR_COMPANIES.find(c => c.name.toLowerCase() === editOffer.company.toLowerCase())
      return match?.levels || []
    }
    return []
  })
  const [showLevelSuggestions, setShowLevelSuggestions] = useState(false)

  const handleSelectCompany = (name: string) => {
    handleCompanyChange(name)
    setShowSuggestions(false)

    // Also prepare level suggestions
    const match = POPULAR_COMPANIES.find(c => c.name.toLowerCase() === name.toLowerCase())
    if (match && match.levels) {
      setLevelSuggestions(match.levels)
    } else {
      setLevelSuggestions([])
    }
  }

  const handleSelectLevel = (level: string) => {
    handleInputChange('level', level)
    setShowLevelSuggestions(false)
  }



  const handleGradeChange = (field: 'wlb_grade' | 'growth_grade' | 'benefits_grade', value: string) => {
    // Update the grade
    setFormData(prev => {
      const updates: any = { [field]: value }

      // Also update the corresponding score if it's WLB or Growth
      if (field === 'wlb_grade') {
        updates.wlb_score = getScoreFromGrade(value)
      } else if (field === 'growth_grade') {
        updates.growth_score = getScoreFromGrade(value)
      }

      return { ...prev, ...updates }
    })
  }

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    const totalCompensation = (formData.base_salary || 0) + (formData.equity || 0) + (formData.bonus || 0)

    const offer: Offer = {
      id: editOffer?.id || Date.now().toString(),
      company: formData.company!,
      position: formData.position!,
      level: formData.level,
      location: formData.location!,
      base_salary: formData.base_salary!,
      equity: formData.equity || 0,
      bonus: formData.bonus || 0,
      signing_bonus: formData.signing_bonus || 0,
      work_type: formData.work_type!,
      employment_type: formData.employment_type!,
      domain: formData.domain,
      benefits_grade: formData.benefits_grade!,
      wlb_grade: formData.wlb_grade,
      wlb_score: formData.wlb_score!,
      growth_grade: formData.growth_grade,
      growth_score: formData.growth_score!,
      // role_fit removed
      job_description: formData.job_description,
      relocation_support: formData.relocation_support,
      other_perks: formData.other_perks,
      total_compensation: totalCompensation
    }

    onSubmit(offer)
  }, [formData, validateForm, onSubmit, editOffer])

  const handleInputChange = useCallback((field: keyof Offer, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }, [errors])

  const handleFileUpload = useCallback(async (file: File) => {
    setIsUploading(true)
    try {
      // Simulate file processing
      await new Promise(resolve => setTimeout(resolve, 2000))

      // Mock extracted data
      const extractedData = {
        company: 'Google',
        position: 'Senior Software Engineer',
        location: 'Mountain View, CA',
        base_salary: 180000,
        equity: 150000,
        bonus: 25000,
        signing_bonus: 50000,
        benefits_grade: 'A+' as const,
        job_description: 'Leading backend development for search infrastructure...'
      }

      setFormData(prev => ({ ...prev, ...extractedData }))
      setActiveTab('manual')
    } catch (error) {
      console.error('File upload failed:', error)
    } finally {
      setIsUploading(false)
    }
  }, [])

  const totalCompensation = (formData.base_salary || 0) + (formData.equity || 0) + (formData.bonus || 0)

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="glass-card w-full max-w-4xl max-h-[90vh] overflow-hidden rounded-2xl border border-white/10 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10 bg-white/5">
          <h3 className="text-xl font-bold text-white">
            {editOffer ? 'Edit Offer' : 'Add New Offer'}
          </h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors text-slate-400 hover:text-white"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-white/10 bg-white/5">
          <button
            onClick={() => setActiveTab('manual')}
            className={`flex-1 py-4 px-4 text-sm font-semibold transition-all relative ${activeTab === 'manual'
              ? 'text-cyan-400 bg-white/5'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
          >
            Manual Entry
            {activeTab === 'manual' && (
              <motion.div
                layoutId="activeTab"
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-cyan-400 to-blue-500"
              />
            )}
          </button>
          <button
            onClick={() => setActiveTab('upload')}
            className={`flex-1 py-4 px-4 text-sm font-semibold transition-all relative ${activeTab === 'upload'
              ? 'text-cyan-400 bg-white/5'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
          >
            Upload Offer Letter
            {activeTab === 'upload' && (
              <motion.div
                layoutId="activeTab"
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-cyan-400 to-blue-500"
              />
            )}
          </button>
        </div>

        <div className="overflow-y-auto max-h-[calc(90vh-140px)] custom-scrollbar">
          {activeTab === 'upload' ? (
            <div className="p-8">
              <FileUpload
                onFileUpload={handleFileUpload}
                acceptedTypes={['application/pdf', '.doc', '.docx']}
                maxSize={10 * 1024 * 1024} // 10MB
                placeholder="Drag & drop your offer letter here"
                isProcessing={isUploading}
              />

              {isUploading && (
                <div className="mt-4 p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl">
                  <div className="flex items-center space-x-3">
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-blue-500 border-t-transparent"></div>
                    <span className="text-sm text-blue-300">Processing your offer letter...</span>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="p-8 space-y-8">
              {/* Basic Information */}
              <div className="space-y-4">
                <h4 className="text-sm font-semibold uppercase tracking-wider text-slate-500">Core Details</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Company *</label>
                    <div className="relative group">
                      <input
                        type="text"
                        value={formData.company || ''}
                        onChange={(e) => handleCompanyChange(e.target.value)}
                        onFocus={() => {
                          if (formData.company && formData.company.length > 0) {
                            setShowSuggestions(true)
                          }
                        }}
                        onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                        className={`w-full px-4 py-3 bg-white/5 border rounded-xl text-white placeholder-slate-500 focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all ${errors.company ? 'border-red-500/50 focus:ring-red-500' : 'border-white/10 hover:border-white/20'
                          }`}
                        placeholder="e.g., Google, Microsoft"
                        autoComplete="off"
                      />

                      {/* Custom Autocomplete Dropdown */}
                      {showSuggestions && suggestions.length > 0 && (
                        <motion.div
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="absolute z-50 left-0 right-0 mt-2 bg-slate-900 border border-white/10 rounded-xl shadow-xl overflow-hidden max-h-60 overflow-y-auto custom-scrollbar ring-1 ring-white/5"
                        >
                          {suggestions.map((company) => (
                            <button
                              key={company.name}
                              type="button"
                              className="w-full text-left px-4 py-3 text-sm text-slate-300 hover:text-white hover:bg-cyan-500/20 transition-colors flex items-center justify-between group/item"
                              onMouseDown={(e) => {
                                e.preventDefault() // Prevent blur
                                handleSelectCompany(company.name)
                              }}
                            >
                              <span className="font-medium">{company.name}</span>
                              <div className="flex space-x-2 text-[10px] uppercase opacity-50 group-hover/item:opacity-100 transition-opacity">
                                {company.wlb_grade && <span className="px-1.5 py-0.5 rounded bg-white/5 border border-white/5">WLB: {company.wlb_grade}</span>}
                                {company.growth_grade && <span className="px-1.5 py-0.5 rounded bg-white/5 border border-white/5">Growth: {company.growth_grade}</span>}
                              </div>
                            </button>
                          ))}
                        </motion.div>
                      )}
                    </div>
                    {errors.company && <p className="mt-1 text-sm text-red-400">{errors.company}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Position *</label>
                    <input
                      type="text"
                      value={formData.position || ''}
                      onChange={(e) => handleInputChange('position', e.target.value)}
                      className={`w-full px-4 py-3 bg-white/5 border rounded-xl text-white placeholder-slate-500 focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all ${errors.position ? 'border-red-500/50 focus:ring-red-500' : 'border-white/10 hover:border-white/20'
                        }`}
                      placeholder="e.g., Senior Software Engineer"
                    />
                    {errors.position && <p className="mt-1 text-sm text-red-400">{errors.position}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Location *</label>
                    <input
                      type="text"
                      value={formData.location || ''}
                      onChange={(e) => handleInputChange('location', e.target.value)}
                      className={`w-full px-4 py-3 bg-white/5 border rounded-xl text-white placeholder-slate-500 focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all ${errors.location ? 'border-red-500/50 focus:ring-red-500' : 'border-white/10 hover:border-white/20'
                        }`}
                      placeholder="e.g., San Francisco, CA"
                    />
                    {errors.location && <p className="mt-1 text-sm text-red-400">{errors.location}</p>}
                  </div>

                  <div className="relative group">
                    <label className="block text-sm font-medium text-slate-300 mb-2">Job Level (e.g. 61, IC3)</label>
                    <input
                      type="text"
                      value={formData.level || ''}
                      onChange={(e) => handleInputChange('level', e.target.value)}
                      onFocus={() => {
                        if (levelSuggestions.length > 0) {
                          setShowLevelSuggestions(true)
                        }
                      }}
                      onBlur={() => setTimeout(() => setShowLevelSuggestions(false), 200)}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all hover:border-white/20"
                      placeholder="Optional company level"
                      autoComplete="off"
                    />

                    {/* Level Suggestions Dropdown */}
                    {showLevelSuggestions && levelSuggestions.length > 0 && (
                      <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="absolute z-50 left-0 right-0 mt-2 bg-slate-900 border border-white/10 rounded-xl shadow-xl overflow-hidden max-h-60 overflow-y-auto custom-scrollbar ring-1 ring-white/5"
                      >
                        <div className="px-3 py-2 text-[10px] uppercase font-bold text-slate-500 border-b border-white/5">
                          Common {formData.company} Levels
                        </div>
                        {levelSuggestions.map((level) => (
                          <button
                            key={level}
                            type="button"
                            className="w-full text-left px-4 py-3 text-sm text-slate-300 hover:text-white hover:bg-cyan-500/10 transition-colors"
                            onMouseDown={(e) => {
                              e.preventDefault()
                              handleSelectLevel(level)
                            }}
                          >
                            {level}
                          </button>
                        ))}
                      </motion.div>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Domain</label>
                    <div className="relative">
                      <select
                        value={formData.domain || ''}
                        onChange={(e) => handleInputChange('domain', e.target.value)}
                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:ring-2 focus:ring-cyan-500 focus:border-transparent appearance-none transition-all hover:border-white/20"
                      >
                        <option value="" className="bg-slate-800">Select domain...</option>
                        {DOMAINS.map((domain) => (
                          <option key={domain.value} value={domain.value} className="bg-slate-800">
                            {domain.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              {/* Compensation */}
              <div className="bg-white/5 p-6 rounded-2xl border border-white/10">
                <h4 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                  <span className="p-1 rounded bg-gradient-to-br from-green-500 to-emerald-600">
                    <CurrencyDollarIcon className="h-4 w-4 text-white" />
                  </span>
                  Compensation Details
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Base Salary ($) *</label>
                    <input
                      type="number"
                      value={formData.base_salary || ''}
                      onChange={(e) => handleInputChange('base_salary', parseInt(e.target.value) || 0)}
                      className={`w-full px-4 py-3 bg-black/20 border rounded-xl text-white placeholder-slate-500 focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all ${errors.base_salary ? 'border-red-500/50' : 'border-white/10 hover:border-white/20'
                        }`}
                      placeholder="150000"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Equity/Stock ($/yr)</label>
                    <input
                      type="number"
                      value={formData.equity || ''}
                      onChange={(e) => handleInputChange('equity', parseInt(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-black/20 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all hover:border-white/20"
                      placeholder="50000"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Annual Bonus ($)</label>
                    <input
                      type="number"
                      value={formData.bonus || ''}
                      onChange={(e) => handleInputChange('bonus', parseInt(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-black/20 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all hover:border-white/20"
                      placeholder="25000"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Signing Bonus ($)</label>
                    <input
                      type="number"
                      value={formData.signing_bonus || ''}
                      onChange={(e) => handleInputChange('signing_bonus', parseInt(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-black/20 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all hover:border-white/20"
                      placeholder="15000"
                    />
                  </div>
                </div>

                {totalCompensation > 0 && (
                  <div className="mt-6 p-4 bg-green-500/10 border border-green-500/20 rounded-xl">
                    <p className="text-sm font-medium text-green-400 flex justify-between items-center">
                      <span>Total Annual Compensation</span>
                      <span className="text-xl font-bold">${totalCompensation.toLocaleString()}</span>
                    </p>
                  </div>
                )}
              </div>

              {/* Work Details & Scores */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-4">
                  <h4 className="text-sm font-semibold uppercase tracking-wider text-slate-500">Role Details</h4>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Work Type</label>
                    <select
                      value={formData.work_type || 'hybrid'}
                      onChange={(e) => handleInputChange('work_type', e.target.value)}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:ring-2 focus:ring-cyan-500 focus:border-transparent appearance-none transition-all hover:border-white/20"
                    >
                      {WORK_TYPES.map((type) => (
                        <option key={type.value} value={type.value} className="bg-slate-800">{type.label}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Benefits Grade</label>
                    <select
                      value={formData.benefits_grade || 'B'}
                      onChange={(e) => handleInputChange('benefits_grade', e.target.value)}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:ring-2 focus:ring-cyan-500 focus:border-transparent appearance-none transition-all hover:border-white/20"
                    >
                      {BENEFITS_GRADES.map((grade) => (
                        <option key={grade.value} value={grade.value} className="bg-slate-800">{grade.label}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="space-y-4">
                  <h4 className="text-sm font-semibold uppercase tracking-wider text-slate-500">Grading & Ratings</h4>
                  <div className="bg-white/5 p-4 rounded-xl border border-white/10 space-y-6">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">WLB Grade</label>
                        <select
                          value={formData.wlb_grade || ''}
                          onChange={(e) => handleGradeChange('wlb_grade', e.target.value)}
                          className="w-full px-3 py-2 bg-slate-800 border border-white/10 rounded-lg text-white text-sm"
                        >
                          <option value="">Auto/None</option>
                          {BENEFITS_GRADES.map(g => <option key={g.value} value={g.value}>{g.value}</option>)}
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Growth Grade</label>
                        <select
                          value={formData.growth_grade || ''}
                          onChange={(e) => handleGradeChange('growth_grade', e.target.value)}
                          className="w-full px-3 py-2 bg-slate-800 border border-white/10 rounded-lg text-white text-sm"
                        >
                          <option value="">Auto/None</option>
                          {BENEFITS_GRADES.map(g => <option key={g.value} value={g.value}>{g.value}</option>)}
                        </select>
                      </div>
                    </div>

                    {/* Sliders removed as per user request - scores are inferred from grades */}
                  </div>
                </div>
              </div>

              {/* Additional Details */}
              <div className="space-y-4">
                <h4 className="text-sm font-semibold uppercase tracking-wider text-slate-500">Notes & Perks</h4>
                <textarea
                  value={formData.other_perks || ''}
                  onChange={(e) => handleInputChange('other_perks', e.target.value)}
                  rows={3}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all hover:border-white/20"
                  placeholder="Additional perks, notes, or thoughts..."
                />
              </div>

              {/* Form Actions */}
              <div className="flex justify-end space-x-4 pt-6 border-t border-white/10">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-6 py-3 text-slate-300 hover:text-white hover:bg-white/5 rounded-xl transition-colors font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-8 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-xl font-bold shadow-lg shadow-blue-500/30 transition-all transform hover:scale-105"
                >
                  {editOffer ? 'Update Offer' : 'Save Offer'}
                </button>
              </div>
            </form>
          )}
        </div>
      </motion.div>
    </motion.div>
  )
}
