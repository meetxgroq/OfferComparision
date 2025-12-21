'use client'

import { useState, useCallback, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import {
  PlusIcon,
  DocumentTextIcon,
  CogIcon,
  ChartBarIcon,
  SparklesIcon,
  CloudArrowUpIcon,
  XMarkIcon,
  AdjustmentsHorizontalIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline'

import ProfileManager from '@/components/ProfileManager'
import AdvancedOfferForm from '@/components/AdvancedOfferForm'
import PreferencesPanel from '@/components/PreferencesPanel'
import OfferCards from '@/components/OfferCards'
import AnalysisResults from '@/components/AnalysisResults'
import { Offer, UserPreferences } from '@/types'

export default function OfferComparePage() {
  const [offers, setOffers] = useState<Offer[]>([])
  const [selectedOffers, setSelectedOffers] = useState<string[]>([])
  const [preferences, setPreferences] = useState<UserPreferences>({
    salary_weight: 0.30,
    equity_weight: 0.20,
    wlb_weight: 0.20,
    growth_weight: 0.15,
    culture_weight: 0.10,
    benefits_weight: 0.05
  })
  const [error, setError] = useState<string | null>(null)
  const [analysisResults, setAnalysisResults] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [showProfileModal, setShowProfileModal] = useState(false)
  const [showPreferencesModal, setShowPreferencesModal] = useState(false)
  const [showOfferModal, setShowOfferModal] = useState(false)

  // Load data from localStorage on component mount
  useEffect(() => {
    const savedOffers = localStorage.getItem('offercompare_offers')
    const savedPreferences = localStorage.getItem('offercompare_preferences')
    const savedSelectedOffers = localStorage.getItem('offercompare_selected_offers')

    if (savedOffers) {
      try {
        const parsedOffers = JSON.parse(savedOffers)
        if (Array.isArray(parsedOffers)) {
          setOffers(parsedOffers.map((o: any) => ({ ...o, id: String(o.id) })))
        }
      } catch (error) {
        console.error('Error loading saved offers:', error)
      }
    }

    if (savedPreferences) {
      try {
        const parsedPreferences = JSON.parse(savedPreferences)
        if (parsedPreferences && typeof parsedPreferences === 'object') {
          setPreferences(prevPrefs => ({ ...prevPrefs, ...parsedPreferences }))
        }
      } catch (error) {
        console.error('Error loading saved preferences:', error)
      }
    }

    if (savedSelectedOffers) {
      try {
        const parsedSelected = JSON.parse(savedSelectedOffers)
        if (Array.isArray(parsedSelected)) {
          setSelectedOffers(parsedSelected.map(String))
        }
      } catch (error) {
        console.error('Error loading saved selected offers:', error)
      }
    }
  }, [])

  // Save offers to localStorage whenever they change
  useEffect(() => {
    if (offers.length > 0) {
      localStorage.setItem('offercompare_offers', JSON.stringify(offers))
    }
  }, [offers])

  // Save preferences to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('offercompare_preferences', JSON.stringify(preferences))
  }, [preferences])

  // Save selected offers to localStorage whenever they change
  useEffect(() => {
    if (selectedOffers.length > 0) {
      localStorage.setItem('offercompare_selected_offers', JSON.stringify(selectedOffers))
    }
  }, [selectedOffers])

  const handleAddOffer = useCallback((newOffer: Offer) => {
    setOffers(prev => [...prev, { ...newOffer, id: Date.now().toString() }])
    setShowOfferModal(false)
  }, [])

  const handleRemoveOffer = useCallback((offerId: string) => {
    setOffers(prev => prev.filter(offer => offer.id !== offerId))
    setSelectedOffers(prev => prev.filter(id => id !== offerId))
  }, [])

  const handleToggleSelection = useCallback((offerId: string) => {
    setSelectedOffers(prev =>
      prev.includes(offerId)
        ? prev.filter(id => id !== offerId)
        : [...prev, offerId]
    )
  }, [])

  const runAnalysis = async () => {
    if (selectedOffers.length < 2) {
      setError('Please select at least 2 offers to compare')
      return
    }

    setIsAnalyzing(true)
    setError(null)

    try {
      const selectedOfferData = offers.filter(offer => selectedOffers.includes(offer.id))
      const response = await axios.post('http://localhost:8001/api/analyze', {
        offers: selectedOfferData,
        user_preferences: preferences
      })
      setAnalysisResults(response.data)
      // Scroll to results
      setTimeout(() => {
        document.getElementById('analysis-results')?.scrollIntoView({ behavior: 'smooth' })
      }, 100)
    } catch (error: any) {
      console.error('Analysis failed:', error)
      let errorMessage = 'Analysis failed. Please try again.'

      const detail = error.response?.data?.detail
      if (typeof detail === 'string') {
        errorMessage = detail
      } else if (detail && typeof detail === 'object') {
        errorMessage = JSON.stringify(detail)
      } else if (error.message) {
        errorMessage = error.message
      }

      if (errorMessage.toLowerCase().includes('api key')) {
        errorMessage += ' Tip: Please check your .env file and ensure you have a valid API key set.'
      }

      setError(errorMessage)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleClearAllData = useCallback(() => {
    if (confirm('Are you sure you want to clear all saved offers and preferences? This action cannot be undone.')) {
      localStorage.removeItem('offercompare_offers')
      localStorage.removeItem('offercompare_preferences')
      localStorage.removeItem('offercompare_selected_offers')
      setOffers([])
      setSelectedOffers([])
      setPreferences({
        salary_weight: 0.30,
        equity_weight: 0.20,
        wlb_weight: 0.20,
        growth_weight: 0.15,
        culture_weight: 0.10,
        benefits_weight: 0.05
      })
      setAnalysisResults(null)
      setError(null)
      alert('All data cleared successfully!')
    }
  }, [])

  return (
    <div className="min-h-screen font-sans selection:bg-cyan-500/30">

      {/* Dynamic Background Blob */}
      <div className="fixed top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-500/10 rounded-full blur-3xl animate-blob"></div>
        <div className="absolute top-[20%] right-[-10%] w-[40%] h-[40%] bg-cyan-500/10 rounded-full blur-3xl animate-blob animation-delay-2000"></div>
        <div className="absolute bottom-[-10%] left-[20%] w-[50%] h-[50%] bg-blue-500/10 rounded-full blur-3xl animate-blob animation-delay-4000"></div>
      </div>

      {/* Header */}
      <header className="glass sticky top-0 z-40 border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <div className="flex items-center space-x-4">
              <div className="bg-gradient-to-br from-cyan-500 to-blue-600 p-2.5 rounded-xl shadow-lg shadow-cyan-500/20">
                <ChartBarIcon className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white via-cyan-100 to-blue-200">
                  OfferCompare Pro
                </h1>
                <p className="text-xs text-slate-400 font-medium tracking-wider">INTELLIGENT CAREER ANALYSIS</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <button
                onClick={handleClearAllData}
                className="text-slate-400 hover:text-red-400 transition-colors p-2"
                title="Clear All Data"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-12">

        {/* Helper Cards Section (Profile & Preferences) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-card rounded-2xl p-6 relative group overflow-hidden cursor-pointer"
            onClick={() => setShowProfileModal(true)}
          >
            <div className="absolute top-0 right-0 p-4 opacity-50 group-hover:opacity-100 transition-opacity">
              <ArrowRightIcon className="h-5 w-5 text-cyan-400" />
            </div>
            <div className="flex items-start space-x-4">
              <div className="p-3 bg-blue-500/10 rounded-xl text-blue-400 group-hover:bg-blue-500/20 transition-colors">
                <DocumentTextIcon className="h-8 w-8" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white group-hover:text-blue-200 transition-colors">Your Profile</h3>
                <p className="text-slate-400 text-sm mt-1">Upload your resume to get personalized AI recommendations tailored to your experience.</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass-card rounded-2xl p-6 relative group overflow-hidden cursor-pointer"
            onClick={() => setShowPreferencesModal(true)}
          >
            <div className="absolute top-0 right-0 p-4 opacity-50 group-hover:opacity-100 transition-opacity">
              <ArrowRightIcon className="h-5 w-5 text-purple-400" />
            </div>
            <div className="flex items-start space-x-4">
              <div className="p-3 bg-purple-500/10 rounded-xl text-purple-400 group-hover:bg-purple-500/20 transition-colors">
                <AdjustmentsHorizontalIcon className="h-8 w-8" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white group-hover:text-purple-200 transition-colors">Analysis Preferences</h3>
                <p className="text-slate-400 text-sm mt-1">Customize how we weigh Salary, Equity, WLB, and Culture in our scoring engine.</p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Offers Section */}
        <section className="space-y-6">
          <div className="flex justify-between items-end">
            <div>
              <h2 className="text-3xl font-bold text-white flex items-center gap-3">
                <span className="w-2 h-8 bg-gradient-to-b from-cyan-400 to-blue-600 rounded-full block"></span>
                Your Job Offers
              </h2>
              <p className="text-slate-400 mt-2 ml-5">Compare your opportunities side-by-side.</p>
            </div>

            <button
              onClick={() => setShowOfferModal(true)}
              className="glass-button px-6 py-3 rounded-xl flex items-center gap-2 font-semibold group shadow-lg shadow-cyan-900/20"
            >
              <PlusIcon className="h-5 w-5 group-hover:rotate-90 transition-transform duration-300" />
              <span>Add Offer</span>
            </button>
          </div>

          {offers.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="glass-card rounded-3xl p-16 text-center border-dashed border-2 border-slate-700/50"
            >
              <div className="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mx-auto mb-6">
                <CloudArrowUpIcon className="h-10 w-10 text-slate-500" />
              </div>
              <h3 className="text-xl font-medium text-white mb-2">No offers added yet</h3>
              <p className="text-slate-400 mb-8 max-w-md mx-auto">Start by adding your first job offer to verify compensation details and get AI insights.</p>
              <button
                onClick={() => setShowOfferModal(true)}
                className="px-8 py-3 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl font-medium transition-all shadow-lg shadow-cyan-900/30"
              >
                Add Your First Offer
              </button>
            </motion.div>
          ) : (
            <div className="space-y-8">
              <OfferCards
                offers={offers}
                selectedOffers={selectedOffers}
                onToggleSelection={handleToggleSelection}
                onRemoveOffer={handleRemoveOffer}
              />

              <div className="glass-card p-4 rounded-xl flex flex-col sm:flex-row items-center justify-between gap-4 border-l-4 border-l-cyan-500">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center border border-slate-700">
                    <span className="text-xl font-bold text-white">{selectedOffers.length}</span>
                  </div>
                  <div>
                    <h4 className="text-white font-medium">Offers Selected for Comparison</h4>
                    <p className="text-slate-400 text-sm">Select at least 2 offers to unlock AI analysis.</p>
                  </div>
                </div>

                <div className="flex flex-col items-end gap-2">
                  <button
                    onClick={runAnalysis}
                    disabled={selectedOffers.length < 2 || isAnalyzing}
                    className={`
                      px-8 py-4 rounded-xl font-bold text-lg flex items-center gap-3 transition-all min-w-[200px] justify-center
                      ${selectedOffers.length >= 2
                        ? 'bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white shadow-xl shadow-blue-900/30'
                        : 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'}
                    `}
                  >
                    {isAnalyzing ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        <span>Analyzing...</span>
                      </>
                    ) : (
                      <>
                        <SparklesIcon className="h-6 w-6" />
                        <span>Run Comparison</span>
                      </>
                    )}
                  </button>
                  {error && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="text-red-400 text-sm bg-red-900/20 border border-red-500/30 px-4 py-2 rounded-lg max-w-md text-right"
                    >
                      {error}
                    </motion.div>
                  )}
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Analysis Results */}
        <AnimatePresence>
          {analysisResults && (
            <motion.div
              id="analysis-results"
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ duration: 0.5 }}
            >
              <div className="flex items-center gap-3 mb-8">
                <span className="w-2 h-8 bg-gradient-to-b from-purple-400 to-pink-600 rounded-full block"></span>
                <h2 className="text-3xl font-bold text-white">AI Analysis Results</h2>
              </div>
              <AnalysisResults results={analysisResults} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Modals */}
      <AnimatePresence>
        {showProfileModal && (
          <ProfileManager onClose={() => setShowProfileModal(false)} />
        )}

        {showPreferencesModal && (
          <PreferencesPanel
            preferences={preferences}
            onSave={setPreferences}
            onClose={() => setShowPreferencesModal(false)}
          />
        )}

        {showOfferModal && (
          <AdvancedOfferForm
            onSubmit={handleAddOffer}
            onClose={() => setShowOfferModal(false)}
          />
        )}
      </AnimatePresence>
    </div>
  )
}