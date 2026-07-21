import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Trophy, Award, Star, Flame, Zap, BookOpen, GraduationCap, Target, CheckCircle2, Briefcase, Loader2,
} from 'lucide-react'

const API = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`

const ICONS = { Trophy, Award, Star, Flame, Zap, BookOpen, GraduationCap, Target, CheckCircle2, Briefcase }

function BadgeIcon({ name, className }) {
  const Icon = ICONS[name] || Award
  return <Icon className={className} />
}

export function BadgeGrid({ token }) {
  const [badges, setBadges] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API}/users/me/badges`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(d => {
        setBadges(d.badges ?? [])
        setLoading(false)
      })
      .catch(e => {
        console.error(e)
        setLoading(false)
      })
  }, [token])

  if (loading) {
    return <div className="h-32 flex items-center justify-center"><Loader2 className="w-6 h-6 animate-spin text-cyan" /></div>
  }

  return (
    <div className="grid grid-cols-3 sm:grid-cols-4 gap-3">
      {badges.map(b => (
        <div
          key={b.key}
          title={b.description}
          className={`flex flex-col items-center gap-2 p-3 rounded-2xl border transition-all ${
            b.earned
              ? 'bg-blue/10 border-blue/20 text-blue shadow-blue-glow-sm'
              : 'border-white/10 text-slate-500 grayscale opacity-30'
          }`}
        >
          <BadgeIcon name={b.icon} className="w-6 h-6" />
          <span className="text-[10px] uppercase tracking-widest font-mono text-center leading-tight">{b.name}</span>
        </div>
      ))}
    </div>
  )
}

export function AchievementToast({ badge, onDismiss }) {
  useEffect(() => {
    const t = setTimeout(onDismiss, 4000)
    return () => clearTimeout(t)
  }, [onDismiss])

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className="glass-card shadow-blue-glow flex items-center gap-3 p-4 rounded-2xl border-blue/30 bg-base/95 w-72 pointer-events-auto"
    >
      <div className="w-10 h-10 rounded-2xl bg-blue/10 border border-blue/20 flex items-center justify-center shrink-0">
        <BadgeIcon name={badge.icon} className="w-5 h-5 text-blue" />
      </div>
      <div className="min-w-0">
        <p className="text-[10px] uppercase tracking-widest font-mono text-blue">Badge Unlocked</p>
        <p className="text-sm font-bold text-white truncate">{badge.name}</p>
        <p className="text-xs text-slate-400 truncate">{badge.description}</p>
      </div>
    </motion.div>
  )
}
