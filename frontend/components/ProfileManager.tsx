'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { XMarkIcon, UserIcon, DocumentTextIcon } from '@heroicons/react/24/outline'
import FileUpload from './FileUpload'

interface ProfileManagerProps {
  onClose: () => void
}

export default function ProfileManager({ onClose }: ProfileManagerProps) {
  const [profile, setProfile] = useState({
    name: '',
    email: '',
    experience_years: 0,
    current_location: '',
    skills: [] as string[],
    resume_text: ''
  })
  const [isUploading, setIsUploading] = useState(false)

  const handleResumeUpload = async (file: File) => {
    setIsUploading(true)
    try {
      // Simulate resume processing
      await new Promise(resolve => setTimeout(resolve, 3000))

      // Mock extracted profile data
      const extractedProfile = {
        name: 'John Doe',
        email: 'john@example.com',
        experience_years: 5,
        current_location: 'San Francisco, CA',
        skills: ['JavaScript', 'React', 'Node.js', 'Python', 'AWS'],
        resume_text: 'Senior Software Engineer with 5+ years of experience...'
      }

      setProfile(prev => ({ ...prev, ...extractedProfile }))
    } catch (error) {
      console.error('Resume upload failed:', error)
    } finally {
      setIsUploading(false)
    }
  }

  const handleSave = () => {
    // Save profile logic here
    console.log('Saving profile:', profile)
    onClose()
  }

  return (
    <motion.div
      initial={{ opacity: 0, pointerEvents: "none" }}
      animate={{ opacity: 1, pointerEvents: "auto" }}
      exit={{ opacity: 0, pointerEvents: "none" }}
      className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="glass-card w-full max-w-3xl max-h-[90vh] flex flex-col rounded-2xl border border-white/10 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex-none flex items-center justify-between p-6 border-b border-white/10 bg-white/5">
          <h3 className="text-xl font-bold text-white flex items-center gap-3">
            <span className="p-2 rounded-lg bg-gradient-to-br from-blue-600 to-cyan-600">
              <UserIcon className="h-5 w-5 text-white" />
            </span>
            Your Profile
          </h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors text-slate-400 hover:text-white"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto min-h-0 p-8 custom-scrollbar">
          {/* Resume Upload Section */}
          <div className="mb-10 bg-white/5 p-6 rounded-2xl border border-white/10">
            <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <DocumentTextIcon className="h-5 w-5 text-cyan-400" />
              Upload Your Resume
            </h4>
            <FileUpload
              onFileUpload={handleResumeUpload}
              acceptedTypes={['application/pdf', '.doc', '.docx']}
              maxSize={10 * 1024 * 1024} // 10MB
              placeholder="Drag & drop your resume here"
              isProcessing={isUploading}
            />

            {isUploading && (
              <div className="mt-4 p-4 bg-cyan-500/10 border border-cyan-500/20 rounded-xl">
                <div className="flex items-center space-x-3">
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-cyan-500 border-t-transparent"></div>
                  <span className="text-sm text-cyan-300">
                    AI extracting skills and experience...
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Profile Information */}
          <div className="space-y-6">
            <h4 className="text-sm font-semibold uppercase tracking-wider text-slate-500">Personal Details</h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Full Name</label>
                <input
                  type="text"
                  value={profile.name}
                  onChange={(e) => setProfile(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full px-4 py-3 bg-black/20 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all hover:border-white/20"
                  placeholder="John Doe"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Email</label>
                <input
                  type="email"
                  value={profile.email}
                  onChange={(e) => setProfile(prev => ({ ...prev, email: e.target.value }))}
                  className="w-full px-4 py-3 bg-black/20 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all hover:border-white/20"
                  placeholder="john@example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Years of Experience</label>
                <input
                  type="number"
                  value={profile.experience_years}
                  onChange={(e) => setProfile(prev => ({ ...prev, experience_years: parseInt(e.target.value) || 0 }))}
                  className="w-full px-4 py-3 bg-black/20 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all hover:border-white/20"
                  placeholder="5"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Current Location</label>
                <input
                  type="text"
                  value={profile.current_location}
                  onChange={(e) => setProfile(prev => ({ ...prev, current_location: e.target.value }))}
                  className="w-full px-4 py-3 bg-black/20 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all hover:border-white/20"
                  placeholder="San Francisco, CA"
                />
              </div>
            </div>

            {/* Skills */}
            <div className="pt-4">
              <label className="block text-sm font-medium text-slate-300 mb-2">Skills & Technologies</label>
              <div className="flex flex-wrap gap-2 mb-3">
                {profile.skills.map((skill, index) => (
                  <span
                    key={index}
                    className="bg-cyan-500/10 text-cyan-300 px-3 py-1.5 rounded-lg text-sm font-medium flex items-center border border-cyan-500/20"
                  >
                    {skill}
                    <button
                      onClick={() => setProfile(prev => ({
                        ...prev,
                        skills: prev.skills.filter((_, i) => i !== index)
                      }))}
                      className="ml-2 text-cyan-400 hover:text-white transition-colors"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
              <input
                type="text"
                placeholder="Add skills (press Enter)"
                className="w-full px-4 py-3 bg-black/20 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all hover:border-white/20"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    const value = e.currentTarget.value.trim()
                    if (value && !profile.skills.includes(value)) {
                      setProfile(prev => ({ ...prev, skills: [...prev.skills, value] }))
                      e.currentTarget.value = ''
                    }
                  }
                }}
              />
            </div>

            {/* Resume Text Preview */}
            {profile.resume_text && (
              <div className="pt-4">
                <label className="block text-sm font-medium text-slate-300 mb-2">Resume Summary</label>
                <div className="bg-black/30 border border-white/10 rounded-xl p-4 max-h-40 overflow-y-auto text-sm text-slate-400 custom-scrollbar">
                  <p>{profile.resume_text}</p>
                </div>
              </div>
            )}
          </div>
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
            className="px-8 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-xl font-bold shadow-lg shadow-blue-500/30 transition-all transform hover:scale-105"
          >
            Save Profile
          </button>
        </div>
      </motion.div>
    </motion.div>
  )
}
