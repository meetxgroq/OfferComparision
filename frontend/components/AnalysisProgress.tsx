'use client'

import { useState, useEffect, useRef, type ComponentType, type SVGProps } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  DocumentTextIcon,
  CurrencyDollarIcon,
  ShieldCheckIcon,
  ArrowTrendingUpIcon,
  CalculatorIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline'

interface Stage {
  title: string
  subtitle: string
  icon: ComponentType<SVGProps<SVGSVGElement>>
  durationQuick: number
  durationDeep: number
}

const STAGES: Stage[] = [
  {
    title: 'Reviewing your offers',
    subtitle: 'Looking at compensation structures and benefits',
    icon: DocumentTextIcon,
    durationQuick: 5000,
    durationDeep: 8000,
  },
  {
    title: 'Analyzing compensation',
    subtitle: 'Normalizing salaries, equity, and bonuses across markets',
    icon: CurrencyDollarIcon,
    durationQuick: 8000,
    durationDeep: 15000,
  },
  {
    title: 'Comparing benefits & perks',
    subtitle: 'Evaluating healthcare, PTO, retirement, and more',
    icon: ShieldCheckIcon,
    durationQuick: 8000,
    durationDeep: 15000,
  },
  {
    title: 'Evaluating growth potential',
    subtitle: 'Assessing career trajectory and company outlook',
    icon: ArrowTrendingUpIcon,
    durationQuick: 8000,
    durationDeep: 15000,
  },
  {
    title: 'Crunching the numbers',
    subtitle: 'Building side-by-side breakdown for you',
    icon: CalculatorIcon,
    durationQuick: 8000,
    durationDeep: 15000,
  },
  {
    title: 'Preparing your insights',
    subtitle: 'Putting together personalized recommendations',
    icon: SparklesIcon,
    durationQuick: 999999,
    durationDeep: 999999,
  },
]

const FUN_FACTS = [
  'Tip: Always negotiate your first offer — most companies expect it.',
  'Did you know? Equity refreshers can significantly boost total comp over 4 years.',
  'Pro tip: Compare offers using total compensation, not just base salary.',
  'Insight: Remote work flexibility can be worth $10K–$30K in equivalent salary.',
  'Did you know? Sign-on bonuses are often the easiest component to negotiate.',
  'Tip: Ask about 401(k) matching — it\'s essentially free money.',
  'Insight: Companies with higher RSU grants often have lower base salaries by design.',
  'Pro tip: Consider cost-of-living differences when comparing offers across cities.',
  'Did you know? Most tech companies review compensation bands annually.',
  'Tip: Don\'t forget to factor in health insurance premiums when comparing offers.',
]

interface AnalysisProgressProps {
  isDeepAnalysis: boolean
}

export default function AnalysisProgress({ isDeepAnalysis }: AnalysisProgressProps) {
  const [currentStage, setCurrentStage] = useState(0)
  const [elapsed, setElapsed] = useState(0)
  const [factIndex, setFactIndex] = useState(() => Math.floor(Math.random() * FUN_FACTS.length))
  const startTime = useRef(Date.now())

  useEffect(() => {
    setCurrentStage(0)
    const durations = STAGES.map(s => isDeepAnalysis ? s.durationDeep : s.durationQuick)
    let accumulated = 0
    const timeouts: ReturnType<typeof setTimeout>[] = []

    for (let i = 0; i < durations.length - 1; i++) {
      accumulated += durations[i]
      const stageIdx = i + 1
      timeouts.push(setTimeout(() => setCurrentStage(stageIdx), accumulated))
    }

    return () => timeouts.forEach(clearTimeout)
  }, [isDeepAnalysis])

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startTime.current) / 1000))
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const interval = setInterval(() => {
      setFactIndex(prev => (prev + 1) % FUN_FACTS.length)
    }, 6000)
    return () => clearInterval(interval)
  }, [])

  const stage = STAGES[currentStage]
  const Icon = stage.icon
  const totalStages = STAGES.length
  const progressPercent = Math.min(((currentStage + 1) / totalStages) * 100, 95)
  const minutes = Math.floor(elapsed / 60)
  const seconds = elapsed % 60

  const accentGradient = isDeepAnalysis
    ? 'from-purple-500 to-indigo-500'
    : 'from-cyan-500 to-blue-500'
  const glowColor = isDeepAnalysis ? 'shadow-purple-500/20' : 'shadow-cyan-500/20'
  const iconBg = isDeepAnalysis ? 'bg-purple-500/10' : 'bg-cyan-500/10'

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.5 }}
      className={`glass-card rounded-2xl overflow-hidden shadow-2xl ${glowColor}`}
    >
      <div
        className="h-1 bg-slate-800 w-full"
        role="progressbar"
        aria-valuenow={Math.round(progressPercent)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Analysis progress"
      >
        <motion.div
          className={`h-full bg-gradient-to-r ${accentGradient}`}
          initial={{ width: '0%' }}
          animate={{ width: `${progressPercent}%` }}
          transition={{ duration: 1.2, ease: 'easeInOut' }}
        />
      </div>

      <div className="p-8 space-y-6">
        <div className="flex items-center justify-center gap-2">
          {STAGES.map((_, i) => (
            <div
              key={i}
              className={`h-1.5 rounded-full transition-all duration-500 ${
                i < currentStage
                  ? `w-6 bg-gradient-to-r ${accentGradient}`
                  : i === currentStage
                    ? `w-8 bg-gradient-to-r ${accentGradient} animate-pulse`
                    : 'w-1.5 bg-slate-700'
              }`}
            />
          ))}
        </div>

        <div className="min-h-[100px] flex items-center justify-center">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStage}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
              className="flex flex-col items-center text-center gap-3"
            >
              <div
                className={`p-3 rounded-xl ${iconBg} border border-white/5`}
                aria-hidden="true"
              >
                <Icon className="h-8 w-8 text-white animate-pulse" />
              </div>
              <div role="status" aria-live="polite">
                <h3 className="text-xl font-bold text-white">{stage.title}</h3>
                <p className="text-sm text-slate-400 mt-1">{stage.subtitle}</p>
              </div>
            </motion.div>
          </AnimatePresence>
        </div>

        <div className="min-h-[40px] flex items-center justify-center">
          <AnimatePresence mode="wait">
            <motion.p
              key={factIndex}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5 }}
              className="text-xs text-slate-500 italic text-center max-w-md"
            >
              {FUN_FACTS[factIndex]}
            </motion.p>
          </AnimatePresence>
        </div>

        <div className="flex justify-end">
          <span className="font-mono text-xs text-slate-600">
            {minutes}:{seconds.toString().padStart(2, '0')}
          </span>
        </div>
      </div>
    </motion.div>
  )
}
