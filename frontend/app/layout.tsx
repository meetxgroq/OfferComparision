import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'BenchMarked',
  description: 'AI-powered job offer analysis and decision support',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-800 text-slate-100">
        {children}
      </body>
    </html>
  )
}


