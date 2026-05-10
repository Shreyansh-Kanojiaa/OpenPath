import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence, useScroll, useTransform } from 'framer-motion'
import LandingPage from './LandingPage'
import { LiveTutor } from './features/LiveTutor'
import { OfflineNotesButton } from './features/OfflineNotes'
import { CareerHub } from './features/CareerHub'
import { Bot, Maximize2, Minimize2 } from 'lucide-react'
// ─────────────────────────────────────────────────────────────────────────────
// DESIGN SYSTEM & UTILS
// ─────────────────────────────────────────────────────────────────────────────
const API = `http://${window.location.hostname}:8000`

const FADE_UP = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.3, ease: [0.16, 1, 0.3, 1] }
}

const BENTO_ITEM = {
  initial: { opacity: 0, y: 15 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true },
  transition: { duration: 0.3, ease: [0.16, 1, 0.3, 1] }
}

// ─────────────────────────────────────────────────────────────────────────────
// ICONS (Clean, minimal line style)
// ─────────────────────────────────────────────────────────────────────────────
const Icon = ({ children, className = "w-5 h-5" }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className}>
    {children}
  </svg>
)

const IcoGrid = () => <Icon><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></Icon>
const IcoCompass = () => <Icon><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></Icon>
const IcoPlus = () => <Icon><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></Icon>
const IcoBack = () => <Icon><polyline points="15 18 9 12 15 6"/></Icon>
const IcoCheck = () => <Icon className="w-4 h-4"><polyline points="20 6 9 17 4 12"/></Icon>
const IcoLogout = () => <Icon><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></Icon>
const IcoUser = () => <Icon><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></Icon>

// ─────────────────────────────────────────────────────────────────────────────
// AMBIENT BACKGROUND
// ─────────────────────────────────────────────────────────────────────────────

function AmbientBackground() {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      <motion.div
        animate={{
          x: [0, 80, 0],
          y: [0, 60, 0],
          scale: [1, 1.2, 1],
        }}
        transition={{ duration: 25, repeat: Infinity, ease: 'linear' }}
        className="absolute top-[-10%] left-[-10%] w-[60vw] h-[60vw] rounded-full"
        style={{ background: 'radial-gradient(circle, rgba(122,162,247,0.06) 0%, transparent 60%)' }}
      />
      <motion.div
        animate={{
          x: [0, -60, 0],
          y: [0, 100, 0],
          scale: [1, 1.1, 1],
        }}
        transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
        className="absolute bottom-[-10%] right-[-10%] w-[50vw] h-[50vw] rounded-full"
        style={{ background: 'radial-gradient(circle, rgba(201,169,110,0.06) 0%, transparent 60%)' }}
      />
      <div 
        className="absolute inset-0 opacity-[0.03]" 
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M40 0H0v40h40V0zM20 0v40M40 20H0' stroke='%23ffffff' fill='none' fill-rule='evenodd'/%3E%3C/svg%3E")`,
          maskImage: 'linear-gradient(to bottom, transparent, black, transparent)',
          WebkitMaskImage: 'linear-gradient(to bottom, transparent, black, transparent)'
        }} 
      />
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// PRIMITIVES
// ─────────────────────────────────────────────────────────────────────────────
function Badge({ children, variant = 'cyan' }) {
  const styles = {
    cyan: 'bg-blue/10 border-blue/20 text-blue',
    success: 'bg-mastered/10 border-mastered/20 text-mastered',
    danger: 'bg-rose-500/10 border-rose-500/20 text-rose-400',
    muted: 'bg-slate-500/10 border-slate-500/20 text-slate-400',
  }
  return (
    <span className={`text-[10px] uppercase tracking-widest px-2 py-0.5 rounded border font-mono ${styles[variant] || styles.cyan}`}>
      {children}
    </span>
  )
}

function ProgressBar({ value = 0, className = "" }) {
  return (
    <div className={`w-full h-1.5 bg-white/5 rounded-[2px] overflow-hidden ${className}`}>
      <motion.div 
        initial={{ width: 0 }}
        whileInView={{ width: `${Math.min(value, 1) * 100}%` }}
        transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
        className="h-full bg-cyan rounded-[2px] shadow-blue-glow-sm"
      />
    </div>
  )
}

function Button({ children, onClick, variant = 'primary', className = "", disabled = false, type = 'button' }) {
  const styles = {
    primary: 'bg-cyan text-base font-semibold hover:shadow-blue-glow hover:scale-[1.02] active:scale-[0.98]',
    outline: 'bg-transparent border border-white/10 text-white hover:bg-white/5',
    ghost: 'bg-transparent text-slate-400 hover:text-white',
    danger: 'bg-transparent border border-rose-500/30 text-rose-400 hover:bg-rose-500/10',
  }
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`px-6 py-2.5 rounded-[2px] text-sm transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed ${styles[variant]} ${className}`}
    >
      {children}
    </button>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// COMPONENTS
// ─────────────────────────────────────────────────────────────────────────────

function NavPill({ active, setPage, user, onLogout }) {
  const [showUser, setShowUser] = useState(false)
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <IcoGrid /> },
    { id: 'discover', label: 'Discover', icon: <IcoCompass /> },
    { id: 'generate', label: 'Generate', icon: <IcoPlus /> },
    { id: 'career', label: 'Career', icon: <Icon><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></Icon> },
  ]

  return (
    <nav className="nav-pill">
      <div className="flex items-center gap-1">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => { setPage(item.id); setShowUser(false) }}
            className={`nav-item ${active === item.id ? 'nav-item-active' : ''}`}
          >
            <span className="flex items-center gap-2 relative z-10">
              {active === item.id && (
                <motion.div
                  layoutId="pill-bg"
                  className="absolute inset-x-[-12px] inset-y-[-4px] bg-white/10 rounded-[2px] z-[-1]"
                  transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                />
              )}
              <span className="opacity-80">{item.icon}</span>
              <span className="hidden md:inline font-display text-xs">{item.label}</span>
            </span>
          </button>
        ))}
        <div className="w-[1px] h-6 bg-white/10 mx-2" />
        <div className="relative">
          <button 
            onClick={() => setShowUser(!showUser)}
            className="w-9 h-9 rounded-[2px] bg-blue/10 border border-blue/20 flex items-center justify-center text-blue hover:bg-blue/20 transition-all overflow-hidden font-display text-sm font-bold"
          >
            {user?.username?.[0].toUpperCase() || 'U'}
          </button>
          <AnimatePresence>
            {showUser && (
              <motion.div 
                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 10, scale: 0.95 }}
                className="absolute right-0 top-full mt-3 w-48 glass rounded p-2 z-[60]"
              >
                <div className="px-3 py-2 mb-2 border-b border-white/5">
                  <div className="text-[10px] text-slate-500 mb-1">Account</div>
                  <div className="text-sm font-display font-semibold truncate">{user?.username}</div>
                </div>
                <button 
                  onClick={onLogout}
                  className="w-full flex items-center gap-2 px-3 py-2 text-xs text-rose-400 hover:bg-rose-500/10 rounded transition-all"
                >
                  <IcoLogout /> Sign out
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </nav>
  )
}

function AuthScreen({ onLogin }) {
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [username, setUsername] = useState('')
  const [confirm, setConfirm] = useState('')
  const [err, setErr] = useState('')
  const [info, setInfo] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErr(''); setInfo(''); setLoading(true)
    try {
      if (mode === 'login') {
        const res = await fetch(`${API}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.detail || 'Login failed')
        localStorage.setItem('op_token', data.access_token)
        onLogin({ username: data.username, user_id: data.user_id, token: data.access_token })
      } else {
        if (password !== confirm) throw new Error('Passwords do not match')
        const res = await fetch(`${API}/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, email, password }),
        })
        if (!res.ok) {
          const data = await res.json()
          throw new Error(data.detail || 'Registration failed')
        }
        setInfo('Account created! You can now sign in.')
        setMode('login')
      }
    } catch (e) {
      setErr(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-base relative">
      <AmbientBackground />
      <div className="hidden lg:flex flex-col justify-center p-20 relative overflow-hidden bg-surface/50 border-r border-white/5 z-10 backdrop-blur-sm">
        <motion.div {...FADE_UP} className="relative z-10">
          <Badge>OpenPath</Badge>
          <h1 className="text-8xl font-bold mt-8 mb-10 leading-tight font-display tracking-tight">
            Learn anything.<br />
            <span className="text-shimmer">Build your path.</span>
          </h1>
          <p className="text-xl text-slate-400 max-w-md leading-relaxed border-l border-blue/30 pl-8 font-sans">
            OpenPath uses AI to build a structured, video-backed learning track for any skill — at any level.
          </p>
        </motion.div>
      </div>

      <div className="flex items-center justify-center p-8 relative z-10">
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-md"
        >
          <div className="glass-card p-10 bg-surface/50">
            <div className="flex bg-white/5 p-1 rounded mb-12 shadow-inner">
              {['login', 'register'].map((m) => (
                <button
                  key={m}
                  onClick={() => { setMode(m); setErr(''); setInfo('') }}
                  className={`flex-1 py-2.5 text-[10px] uppercase tracking-[0.2em] font-display font-bold rounded transition-all ${mode === m ? 'bg-blue text-charcoal-900 shadow-blue-glow' : 'text-slate-500'}`}
                >
                  {m === 'login' ? 'Sign in' : 'Create account'}
                </button>
              ))}
            </div>

            <form onSubmit={handleSubmit} className="space-y-8">
              <AnimatePresence mode="wait">
                <motion.div
                  key={mode}
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -10 }}
                  className="space-y-8"
                >
                  {mode === 'register' && (
                    <div className="space-y-3">
                      <label className="text-[10px] uppercase tracking-[0.3em] text-slate-500 font-mono ml-4">Identifier</label>
                      <input 
                        className="w-full bg-white/5 border border-white/10 rounded px-6 py-4 text-sm font-mono focus:outline-none focus:border-blue/50 focus:ring-1 focus:ring-blue/20 transition-all"
                        placeholder="your_username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                      />
                    </div>
                  )}
                  <div className="space-y-3">
                    <label className="text-[10px] uppercase tracking-[0.3em] text-slate-500 font-mono ml-4">Email</label>
                    <input 
                      type="email"
                      className="w-full bg-white/5 border border-white/10 rounded px-6 py-4 text-sm font-mono focus:outline-none focus:border-blue/50 focus:ring-1 focus:ring-blue/20 transition-all"
                      placeholder="you@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                    />
                  </div>
                  <div className="space-y-3">
                    <label className="text-[10px] uppercase tracking-[0.3em] text-slate-500 font-mono ml-4">Password</label>
                    <input 
                      type="password"
                      className="w-full bg-white/5 border border-white/10 rounded px-6 py-4 text-sm font-mono focus:outline-none focus:border-blue/50 focus:ring-1 focus:ring-blue/20 transition-all"
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                    />
                  </div>
                  {mode === 'register' && (
                    <div className="space-y-3">
                      <label className="text-[10px] uppercase tracking-[0.3em] text-slate-500 font-mono ml-4">Confirm password</label>
                      <input 
                        type="password"
                        className="w-full bg-white/5 border border-white/10 rounded px-6 py-4 text-sm font-mono focus:outline-none focus:border-blue/50 focus:ring-1 focus:ring-blue/20 transition-all"
                        placeholder="••••••••"
                        value={confirm}
                        onChange={(e) => setConfirm(e.target.value)}
                      />
                    </div>
                  )}
                </motion.div>
              </AnimatePresence>

              {info && <p className="text-[11px] text-mastered font-mono px-4">{info}</p>}
              {err && <p className="text-[11px] text-rose-400 font-mono px-4">{err}</p>}

              <Button type="submit" disabled={loading} className="w-full py-5 mt-6 font-display text-base tracking-[0.2em] uppercase">
                {loading ? 'Loading...' : mode === 'login' ? 'Sign in' : 'Create account'}
              </Button>
            </form>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

function Dashboard({ courses, onSelectCourse, user }) {
  const totalCompleted = courses.reduce((acc, c) => acc + c.modules.filter(m => m.is_completed || m.is_skipped).length, 0)
  
  return (
    <div className="max-w-7xl mx-auto px-8 py-32 w-full min-h-screen">
      <header className="mb-16 flex flex-col md:flex-row md:items-end justify-between gap-12">
        <motion.div {...FADE_UP}>
          <p className="text-sm text-slate-500 mb-3">Welcome back,</p>
          <h2 className="text-5xl font-bold font-display tracking-tight">{user?.username}'s courses</h2>
        </motion.div>
        
        <motion.div 
          initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} 
          className="flex gap-12 border-l border-white/10 pl-12 py-2"
        >
          <div>
            <div className="text-4xl font-display font-bold text-white leading-none mb-1">{courses.length}</div>
            <div className="text-xs text-slate-500">Courses</div>
          </div>
          <div>
            <div className="text-4xl font-display font-bold text-blue leading-none mb-1">{totalCompleted}</div>
            <div className="text-xs text-slate-500">Modules done</div>
          </div>
        </motion.div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-6 gap-8">
        {courses.map((course, i) => {
          const completed = course.modules.filter(m => m.is_completed || m.is_skipped).length
          const total = course.modules.length
          const progress = completed / total
          const isLarge = i === 0 || i % 7 === 0

          return (
            <motion.div
              key={course.id}
              {...BENTO_ITEM}
              transition={{ delay: (i % 8) * 0.1 }}
              onClick={() => onSelectCourse(course)}
              onMouseMove={(e) => {
                const rect = e.currentTarget.getBoundingClientRect();
                e.currentTarget.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`);
                e.currentTarget.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`);
              }}
              className={`glass-card p-10 flex flex-col justify-between cursor-pointer group hover:bg-white/[0.08] hover:border-white/20 hover:scale-[1.02] hover:shadow-blue-glow/20 transition-all duration-500 overflow-hidden relative ${isLarge ? 'md:col-span-2 lg:col-span-3 min-h-[420px]' : 'md:col-span-2 lg:col-span-2 min-h-[420px]'}`}
            >
              <div 
                className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none z-0" 
                style={{ background: 'radial-gradient(600px circle at var(--mouse-x, 0) var(--mouse-y, 0), rgba(122,162,247,0.12), transparent 40%)' }}
              />
              
              <div className="space-y-8 relative z-10">
                <div className="flex items-center justify-between">
                  <span className={`text-[10px] px-2.5 py-1 rounded-[2px] font-mono tracking-widest uppercase border ${progress === 1 ? 'bg-mastered/10 text-mastered border-mastered/20' : 'bg-white/5 text-slate-400 border-white/10'}`}>
                    {progress === 1 ? 'Mastered' : course.time_commitment}
                  </span>
                  <span className="text-xs text-slate-500">{Math.round(progress * 100)}%</span>
                </div>
                <h3 className={`font-bold leading-tight font-display transition-colors group-hover:text-cyan ${isLarge ? 'text-4xl' : 'text-2xl'}`}>
                  {course.skill_name}
                </h3>
              </div>

              <div className="space-y-10 relative z-10">
                <div className="flex flex-wrap gap-2">
                  {course.modules.slice(0, 16).map((m, mi) => (
                    <div 
                      key={mi} 
                      className={`w-2 h-2 rounded-[2px] transition-all duration-300 ${m.is_completed || m.is_skipped ? 'bg-mastered shadow-[0_0_8px_rgba(201,169,110,0.4)]' : 'bg-white/10 border border-white/5'}`} 
                    />
                  ))}
                  {course.modules.length > 16 && <span className="text-[10px] text-slate-600 self-center ml-2 font-black">+{course.modules.length - 16}</span>}
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>Progress</span>
                    <span>{completed} / {total} modules</span>
                  </div>
                  <ProgressBar value={progress} />
                </div>
              </div>
            </motion.div>
          )
        })}
        
        <motion.button
          {...BENTO_ITEM}
          transition={{ delay: (courses.length % 8) * 0.1 }}
          className="md:col-span-2 lg:col-span-1 rounded-[2px] border-2 border-dashed border-white/5 hover:border-blue/40 hover:bg-blue/5 transition-all flex flex-col items-center justify-center gap-8 group cursor-pointer min-h-[420px]"
        >
          <div className="w-16 h-16 rounded-[2px] bg-white/5 flex items-center justify-center text-slate-500 group-hover:text-cyan group-hover:scale-105 group-hover:bg-blue/10 transition-all duration-500">
            <IcoPlus />
          </div>
          <span className="text-sm text-slate-500 group-hover:text-cyan transition-colors">New course</span>
        </motion.button>
      </div>
    </div>
  )
}

function SkipQuizPanel({ mod, token, onSkip }) {
  const [phase, setPhase] = useState('idle') // idle | loading | quiz | result
  const [quiz, setQuiz] = useState(null)
  const [current, setCurrent] = useState(0)
  const [score, setScore] = useState(0)
  const [selected, setSelected] = useState(null)
  const [err, setErr] = useState('')

  const startQuiz = async () => {
    setPhase('loading'); setErr('')
    try {
      const res = await fetch(`${API}/generate-quiz?module_id=${mod.id}`, {
        method: 'POST', headers: { Authorization: `Bearer ${token}` }
      })
      if (!res.ok) throw new Error((await res.json()).detail || 'Failed to load quiz')
      setQuiz(await res.json())
      setCurrent(0); setScore(0); setSelected(null)
      setPhase('quiz')
    } catch (e) { setErr(e.message); setPhase('idle') }
  }

  const handleAnswer = async (idx) => {
    if (selected !== null) return
    setSelected(idx)
    const correct = quiz.questions[current].correct_answer_index
    const newScore = idx === correct ? score + 1 : score
    if (idx === correct) setScore(newScore)
    await new Promise(r => setTimeout(r, 900))
    if (current + 1 < quiz.questions.length) {
      setCurrent(c => c + 1); setSelected(null)
    } else {
      const passed = newScore >= 4
      // Submit to backend
      try {
        await fetch(`${API}/submit-quiz?module_id=${mod.id}&score=${newScore}`, {
          method: 'POST', headers: { Authorization: `Bearer ${token}` }
        })
      } catch (_) {}
      if (passed) { onSkip(mod.id, 'skipped') } else { setPhase('result'); }
    }
  }

  if (mod.is_completed || mod.is_skipped) return null

  if (phase === 'idle') return (
    <div className="md:col-span-2 glass-card p-10 flex flex-col justify-center items-center text-center space-y-8 bg-blue/5 border-blue/10 group cursor-pointer hover:bg-blue/10 transition-all duration-500" onClick={startQuiz}>
      <div className="w-20 h-20 rounded bg-blue/10 flex items-center justify-center text-blue group-hover:scale-110 transition-transform duration-700"><IcoCompass /></div>
      <div className="space-y-4">
        <h4 className="text-lg font-black font-display uppercase tracking-[0.2em] text-white">Skip this module</h4>
        <p className="text-xs text-slate-500 font-mono tracking-wide leading-relaxed px-4">Already know this? Take a quick quiz to skip it.</p>
      </div>
      {err && <p className="text-xs text-rose-400 font-mono">{err}</p>}
      <Button variant="outline" className="border-blue/30 text-blue hover:bg-blue/10 shadow-none px-10">Take the quiz</Button>
    </div>
  )

  if (phase === 'loading') return (
    <div className="md:col-span-2 glass-card p-10 flex flex-col items-center justify-center gap-6">
      <motion.div animate={{ rotate: 360 }} transition={{ duration: 1.2, repeat: Infinity, ease: 'linear' }} className="w-10 h-10 border-2 border-blue/30 border-t-blue rounded-full" />
      <p className="text-xs font-mono text-slate-500 uppercase tracking-widest">Generating quiz...</p>
    </div>
  )

  if (phase === 'result') {
    const passed = score >= 4
    return (
      <div className="md:col-span-2 glass-card p-10 flex flex-col items-center justify-center text-center gap-6">
        <div className={`text-4xl font-black font-display ${passed ? 'text-mastered' : 'text-rose-400'}`}>{score}/5</div>
        <p className="text-sm text-slate-400">{passed ? 'Module skipped!' : 'Score 4/5 or higher to skip this module.'}</p>
        <Button variant="outline" onClick={() => setPhase('idle')}>Try again</Button>
      </div>
    )
  }

  if (phase === 'quiz' && quiz) {
    const q = quiz.questions[current]
    return (
      <div className="md:col-span-2 glass-card p-8 flex flex-col gap-6">
        <div className="flex justify-between items-center">
          <span className="text-[10px] font-mono uppercase tracking-widest text-slate-500">Question {current + 1} / {quiz.questions.length}</span>
          <span className="text-[10px] font-mono uppercase tracking-widest text-blue">{score} correct</span>
        </div>
        <p className="text-sm font-semibold text-slate-100 leading-relaxed">{q.question}</p>
        <div className="space-y-2">
          {q.options.map((opt, i) => {
            const isSelected = selected === i
            const isCorrect = selected !== null && i === q.correct_answer_index
            const isWrong = isSelected && i !== q.correct_answer_index
            return (
              <button
                key={i}
                onClick={() => handleAnswer(i)}
                disabled={selected !== null}
                className={`w-full text-left text-xs font-mono px-4 py-3 rounded-[2px] border transition-all duration-300 ${
                  isCorrect ? 'bg-mastered/10 border-mastered/40 text-mastered' :
                  isWrong ? 'bg-rose-500/10 border-rose-500/40 text-rose-400' :
                  isSelected ? 'bg-blue/10 border-blue/40 text-blue' :
                  'bg-transparent border-white/10 text-slate-400 hover:border-white/20 hover:text-slate-200'
                }`}
              >
                {opt}
              </button>
            )
          })}
        </div>
        {selected !== null && (
          <p className="text-[11px] text-slate-500 font-mono italic">{q.explanation}</p>
        )}
      </div>
    )
  }
  return null
}

// ─── WATCH-GATE: YouTube play-tracking + user activity detection ────────────
// Uses YouTube IFrame postMessage API to know when video is actually playing.
// Tracks mouse / keyboard / scroll to detect idleness.
// Only unlocks completion after 80% of the video has been actively watched.
// ────────────────────────────────────────────────────────────────────────────

function WatchGatedVideo({ mod, onComplete, token }) {
  const iframeRef = useRef(null)
  const [ytPlaying, setYtPlaying] = useState(false)       // YouTube player state
  const [watchedSecs, setWatchedSecs] = useState(0)        // accumulated active watch seconds
  const [userActive, setUserActive] = useState(true)        // is user interacting?
  const [canComplete, setCanComplete] = useState(false)
  const idleTimer = useRef(null)
  const tickInterval = useRef(null)
  const IDLE_TIMEOUT = 90_000 // 90 seconds of no interaction → pause counting
  const REQUIRED_RATIO = 0.80

  const videoDuration = mod.video_duration || 600

  // ── YouTube postMessage listener ──
  useEffect(() => {
    const onMessage = (e) => {
      // YouTube sends JSON-encoded state change messages
      if (!e.data || typeof e.data !== 'string') return
      try {
        const data = JSON.parse(e.data)
        // YouTube IFrame API sends event "onStateChange" via postMessage
        // State codes: -1 unstarted, 0 ended, 1 playing, 2 paused, 3 buffering
        if (data.event === 'onStateChange' || data.event === 'infoDelivery') {
          const state = data?.info?.playerState
          if (state === 1) setYtPlaying(true)
          else if (state === 0 || state === 2 || state === -1) setYtPlaying(false)
        }
      } catch (_) {}
    }
    window.addEventListener('message', onMessage)
    return () => window.removeEventListener('message', onMessage)
  }, [])

  // ── Send "listening" command to YouTube player once iframe loads ──
  useEffect(() => {
    const iframe = iframeRef.current
    if (!iframe || !mod.video_id) return
    const sendListen = () => {
      try {
        iframe.contentWindow?.postMessage(
          JSON.stringify({ event: 'listening', id: 1 }),
          'https://www.youtube.com'
        )
      } catch (_) {}
    }
    // Try immediately & a few times after load (player may take a moment)
    sendListen()
    const t1 = setTimeout(sendListen, 1500)
    const t2 = setTimeout(sendListen, 3000)
    const t3 = setTimeout(sendListen, 5000)
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3) }
  }, [mod.video_id])

  // ── User activity tracker ──
  useEffect(() => {
    const resetIdle = () => {
      setUserActive(true)
      clearTimeout(idleTimer.current)
      idleTimer.current = setTimeout(() => setUserActive(false), IDLE_TIMEOUT)
    }
    const events = ['mousemove', 'mousedown', 'keydown', 'scroll', 'touchstart']
    events.forEach(e => window.addEventListener(e, resetIdle, { passive: true }))
    resetIdle() // start the idle timer
    return () => {
      events.forEach(e => window.removeEventListener(e, resetIdle))
      clearTimeout(idleTimer.current)
    }
  }, [])

  // ── Tick watch-time only when video is playing AND user is active ──
  useEffect(() => {
    if (ytPlaying && userActive && !mod.is_completed && !mod.is_skipped) {
      tickInterval.current = setInterval(() => {
        setWatchedSecs(prev => {
          const next = prev + 1
          if (next >= videoDuration * REQUIRED_RATIO) setCanComplete(true)
          return next
        })
      }, 1000)
    } else {
      clearInterval(tickInterval.current)
    }
    return () => clearInterval(tickInterval.current)
  }, [ytPlaying, userActive, mod.is_completed, mod.is_skipped, videoDuration])

  // Reset when switching modules
  useEffect(() => {
    setWatchedSecs(0)
    setCanComplete(false)
    setYtPlaying(false)
  }, [mod.id])

  const pct = Math.min(watchedSecs / (videoDuration * REQUIRED_RATIO), 1)
  const fmtTime = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`

  const handleComplete = async () => {
    try {
      await fetch(`${API}/modules/${mod.id}/complete`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ watch_time: watchedSecs }),
      })
    } catch (_) {}
    onComplete(mod.id, 'watched')
  }

  const isCompleted = mod.is_completed || mod.is_skipped

  return (
    <div className="aspect-video w-full rounded-[40px] overflow-hidden border border-white/5 shadow-2xl relative bg-black shadow-blue-glow/5 group">
      {mod.video_id ? (
        <>
          <iframe
            ref={iframeRef}
            width="100%" height="100%"
            src={`https://www.youtube.com/embed/${mod.video_id}?enablejsapi=1&origin=${encodeURIComponent(window.location.origin)}`}
            title={mod.title} frameBorder="0" allowFullScreen
            allow="autoplay; encrypted-media"
          />

          {/* ── Watch-time HUD overlay ── */}
          {!isCompleted && (
            <div className="absolute bottom-0 left-0 right-0 z-10 pointer-events-none">
              {/* gradient fade from transparent to dark */}
              <div className="h-32 bg-black/80" />
              <div className="bg-black/80 px-10 pb-8 -mt-px pointer-events-auto border-t border-white/5">
                <div className="flex items-center gap-6">
                  {/* Progress ring */}
                  <div className="relative w-14 h-14 flex-shrink-0">
                    <svg viewBox="0 0 44 44" className="w-full h-full -rotate-90">
                      <circle cx="22" cy="22" r="19" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="3" />
                      <motion.circle
                        cx="22" cy="22" r="19" fill="none"
                        stroke={canComplete ? '#c9a96e' : '#7aa2f7'}
                        strokeWidth="3"
                        strokeLinecap="square"
                        strokeDasharray={2 * Math.PI * 19}
                        strokeDashoffset={2 * Math.PI * 19 * (1 - pct)}
                        transition={{ duration: 0.4, ease: 'easeOut' }}
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center text-[10px] font-mono font-bold text-white">
                      {Math.round(pct * 100)}%
                    </div>
                  </div>

                  {/* Status text */}
                  <div className="flex-1 min-w-0">
                    <div className="text-[11px] font-mono uppercase tracking-[0.15em] text-slate-400 mb-1">
                      {canComplete
                        ? '✓ Watch requirement met'
                        : ytPlaying && userActive
                          ? 'Tracking watch time…'
                          : !ytPlaying
                            ? 'Play the video to start tracking'
                            : 'Move your mouse to confirm presence'}
                    </div>
                    <div className="text-[10px] font-mono text-slate-600">
                      {fmtTime(watchedSecs)} watched · {fmtTime(Math.ceil(videoDuration * REQUIRED_RATIO))} required
                    </div>
                  </div>

                  {/* Activity indicators */}
                  <div className="flex items-center gap-3 flex-shrink-0">
                    <div className="flex items-center gap-1.5" title={ytPlaying ? 'Video playing' : 'Video paused'}>
                      <div className={`w-2 h-2 rounded-[2px] transition-colors duration-300 ${ytPlaying ? 'bg-mastered animate-pulse' : 'bg-slate-600'}`} />
                      <span className="text-[9px] font-mono uppercase text-slate-500">{ytPlaying ? 'Playing' : 'Paused'}</span>
                    </div>
                    <div className="w-px h-4 bg-white/10" />
                    <div className="flex items-center gap-1.5" title={userActive ? 'User active' : 'User idle — watching paused'}>
                      <div className={`w-2 h-2 rounded-[2px] transition-colors duration-300 ${userActive ? 'bg-cyan animate-pulse' : 'bg-slate-600'}`} />
                      <span className="text-[9px] font-mono uppercase text-slate-500">{userActive ? 'Active' : 'Idle'}</span>
                    </div>
                  </div>

                  {/* Complete button */}
                  <button
                    disabled={!canComplete}
                    onClick={handleComplete}
                    className={`flex-shrink-0 px-8 py-3 rounded-[2px] text-sm font-bold font-display uppercase tracking-wider transition-all duration-300 ${
                      canComplete
                        ? 'bg-mastered text-black hover:shadow-blue-glow-sm hover:scale-[1.03] cursor-pointer'
                        : 'bg-white/5 text-slate-600 cursor-not-allowed'
                    }`}
                  >
                    {canComplete ? 'Mark complete' : 'Keep watching'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="w-full h-full glass-card flex items-center justify-center flex-col gap-6 text-slate-600 bg-surface">
          <motion.div animate={{ rotate: 360 }} transition={{ duration: 10, repeat: Infinity, ease: 'linear' }} className="w-20 h-20 rounded-[2px] border border-dashed border-white/20 flex items-center justify-center opacity-30"><IcoCompass /></motion.div>
          <p className="font-mono text-xs uppercase tracking-[0.4em]">Loading video...</p>
        </div>
      )}
    </div>
  )
}

function CourseView({ course, onBack, onComplete, onSaveNotes, token }) {
  const mods = course.modules
  const initMod = mods.find(m => !m.is_completed && !m.is_skipped) || mods[0]
  const [activeId, setActiveId] = useState(initMod?.id)
  const activeMod = mods.find(m => m.id === activeId)
  const completedCount = mods.filter(m => m.is_completed || m.is_skipped).length
  const progress = completedCount / mods.length
  const [zenMode, setZenMode] = useState(false)
  const [showTutor, setShowTutor] = useState(false)

  return (
    <div className={`flex w-full overflow-hidden bg-base ${zenMode ? 'fixed inset-0 z-50 pt-0 h-screen' : 'h-screen pt-24'}`}>
      {!zenMode && (
        <aside className="w-96 border-r border-white/5 flex flex-col glass bg-surface/40 backdrop-blur-3xl relative z-20">
        <div className="p-10 border-b border-white/5">
          <button onClick={onBack} className="flex items-center gap-2 text-slate-500 hover:text-white transition-all text-sm mb-8 group">
            <span className="group-hover:-translate-x-1 transition-transform duration-300"><IcoBack /></span> Back
          </button>
          <h2 className="text-2xl font-bold font-display leading-snug mb-6">{course.skill_name}</h2>
          <div className="space-y-4">
             <div className="flex justify-between text-xs text-slate-500">
               <span>Progress</span>
               <span className="text-blue">{Math.round(progress * 100)}%</span>
             </div>
             <ProgressBar value={progress} />
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-2">
          {mods.map((m, i) => {
            const isActive = m.id === activeId
            const isDone = m.is_completed || m.is_skipped
            return (
              <motion.button
                key={m.id}
                onClick={() => setActiveId(m.id)}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: i * 0.05, ease: [0.16, 1, 0.3, 1] }}
                className={`w-full text-left p-4 rounded-[2px] border transition-all duration-300 group relative overflow-hidden ${
                  isActive 
                    ? 'bg-cyan/10 border-cyan/40 text-white shadow-blue-glow-sm' 
                    : 'bg-transparent border-transparent text-slate-500 hover:bg-white/5 hover:text-slate-200'
                }`}
              >
                <div className="flex justify-between items-center mb-2">
                    <span className={`text-[10px] px-2 py-0.5 rounded-[2px] border font-mono tracking-widest uppercase ${
                    isDone ? 'border-mastered/30 text-mastered bg-mastered/10' : 
                    isActive ? 'border-cyan/40 text-cyan bg-cyan/10' : 'border-white/10 text-slate-600'
                  }`}>
                    Module {String(i + 1).padStart(2, '0')}
                  </span>
                  {isDone && <motion.span initial={{ scale: 0 }} animate={{ scale: 1 }} className="text-mastered"><IcoCheck /></motion.span>}
                </div>
                <div className={`text-sm font-bold font-display leading-snug tracking-tight ${isDone ? 'line-through opacity-60' : ''} ${isActive ? 'text-white' : 'group-hover:text-slate-100'}`}>
                  {m.title}
                </div>
              </motion.button>
            )
          })}
        </div>
      </aside>
      )}

      <main className="flex-1 overflow-y-auto custom-scrollbar relative">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeId}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="max-w-5xl mx-auto p-16 lg:p-24"
          >
            {activeMod && (
              <div className="space-y-16">
                <header>
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                    <div className="flex items-center gap-6 text-slate-600">
                      <Badge variant={activeMod.is_completed ? 'success' : 'cyan'}>
                        Module {activeMod.order_index}
                      </Badge>
                      <div className="h-0.5 w-8 bg-white/10" />
                      <span className="font-mono text-[10px] uppercase tracking-[0.3em]">
                        {Math.floor(activeMod.video_duration / 60)}m {activeMod.video_duration % 60}s
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-4">
                      <button onClick={() => setShowTutor(!showTutor)} className="flex items-center gap-2 px-4 py-2 bg-blue/10 text-blue border border-blue/20 hover:bg-blue/20 rounded transition-colors text-sm font-bold shadow-blue-glow/20 shadow-lg">
                        <Bot className="w-4 h-4" /> Live Tutor
                      </button>
                      <OfflineNotesButton moduleId={activeMod.id} token={token} moduleTitle={activeMod.title} />
                      <button onClick={() => setZenMode(!zenMode)} className="flex items-center justify-center w-9 h-9 bg-white/5 hover:bg-white/10 rounded border border-white/10 text-slate-400 transition-colors" title="Toggle Zen Mode">
                        {zenMode ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                  <h1 className="text-4xl font-bold font-display leading-snug mb-6">{activeMod.title}</h1>
                  <p className="text-lg text-slate-400 leading-relaxed font-sans max-w-3xl">{activeMod.description}</p>
                </header>

                <WatchGatedVideo mod={activeMod} onComplete={onComplete} token={token} />

                <div className="grid md:grid-cols-5 gap-10">
                  <div className="md:col-span-3 glass-card p-10 space-y-8 bg-surface/60 transition-all hover:bg-surface/80">
                    <h4 className="text-base font-bold font-display flex items-center gap-3">
                      <span className="text-cyan"><IcoPlus /></span> Notes
                    </h4>
                    <textarea 
                      placeholder="Write your notes here..."
                      defaultValue={activeMod.notes || ''}
                      onBlur={(e) => onSaveNotes(activeMod.id, e.target.value)}
                      className="w-full h-48 bg-white/5 border border-white/5 rounded p-6 text-sm font-mono focus:outline-none focus:border-blue/40 transition-all resize-none shadow-inner"
                    />
                    <div className="flex justify-between items-center px-2">
                       <div className="flex gap-1">
                         {[1,2,3].map(i => <div key={i} className="w-1 h-1 rounded-[2px] bg-cyan/40 animate-pulse" style={{ animationDelay: `${i*200}ms` }} />)}
                       </div>
                      <span className="text-[10px] font-mono text-slate-600 uppercase tracking-[0.3em]">Auto-saved</span>
                    </div>
                  </div>

                  <SkipQuizPanel mod={activeMod} token={token} onSkip={onComplete} />
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
        <AnimatePresence>
          {showTutor && <LiveTutor moduleId={activeMod.id} token={token} onClose={() => setShowTutor(false)} />}
        </AnimatePresence>
      </main>
    </div>
  )
}

function DiscoverPage({ token, onEnroll }) {
  const [courses, setCourses] = useState([])
  const [enrolling, setEnrolling] = useState(null)
  const [loadingCourses, setLoadingCourses] = useState(true)

  useEffect(() => {
    fetch(`${API}/courses/public`)
      .then(r => r.json())
      .then(data => { setCourses(Array.isArray(data) ? data : []); setLoadingCourses(false) })
      .catch(() => setLoadingCourses(false))
  }, [])

  const handleEnroll = async (courseId) => {
    setEnrolling(courseId)
    try {
      const res = await fetch(`${API}/courses/${courseId}/enroll`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) { onEnroll() }
      else { const d = await res.json(); alert(d.detail || 'Could not add course.') }
    } catch { alert('Network error.') }
    setEnrolling(null)
  }

  return (
    <div className="max-w-7xl mx-auto px-8 py-32 w-full min-h-screen">
      <header className="mb-16 px-4">
        <motion.div {...FADE_UP}>
          <Badge>Community</Badge>
          <h1 className="text-4xl font-bold mt-4 font-display tracking-tight leading-none">Discover courses</h1>
          <p className="text-base text-slate-500 mt-4">
            Public learning paths shared by the community. Add one to your dashboard to get started.
          </p>
        </motion.div>
      </header>

      {loadingCourses ? (
        <div className="text-center text-slate-500 py-24">Loading courses...</div>
      ) : courses.length === 0 ? (
        <div className="text-center text-slate-500 py-24">
          <p className="text-lg font-display">No public courses yet.</p>
          <p className="text-sm mt-2">Be the first — generate a course and make it public from your dashboard.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 px-4">
          {courses.map((c, i) => (
            <motion.div
              key={c.id}
              {...BENTO_ITEM}
              transition={{ delay: i * 0.05 }}
              style={{ borderLeft: '3px solid #7aa2f7' }}
              className="glass-card p-8 flex flex-col justify-between min-h-[240px] group border-border/50 bg-surface"
            >
              <div>
                <div className="flex justify-between items-start mb-4 text-xs text-slate-500 font-mono uppercase tracking-wider">
                  <span>{c.module_count} modules</span>
                  <span className="text-blue">{c.current_level}/10 level</span>
                </div>
                <h3 className="text-2xl font-bold font-display leading-tight mb-2">{c.skill_name}</h3>
                <p className="text-sm text-slate-500">by @{c.owner_username} · {c.time_commitment}</p>
              </div>
              <button
                onClick={() => handleEnroll(c.id)}
                disabled={enrolling === c.id}
                className="mt-6 w-full py-2.5 text-sm font-semibold border border-border rounded hover:bg-blue hover:text-base hover:border-blue transition-all duration-200 disabled:opacity-50"
              >
                {enrolling === c.id ? 'Adding...' : 'Add to my courses'}
              </button>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}

const DEPTH_OPTIONS = [
  { value: 'Crash Course (3 modules)', label: 'Crash Course', desc: '3 modules · Quick overview' },
  { value: 'Standard (5 modules)', label: 'Standard', desc: '5 modules · Balanced' },
  { value: 'In-Depth (8 modules)', label: 'In-Depth', desc: '8 modules · Comprehensive' },
]

const TIME_OPTIONS = [
  '1-2 hrs/week', '3-4 hrs/week', '5-7 hrs/week', '8-10 hrs/week', '10+ hrs/week',
]

function GeneratePage({ token, onGenerate, initialSkill = '' }) {
  const [skill, setSkill] = useState(initialSkill)
  const [level, setLevel] = useState(3)
  const [time, setTime] = useState('3-4 hrs/week')
  const [depth, setDepth] = useState('Standard (5 modules)')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleGenerate = async () => {
    if (!skill.trim()) return
    setError('')
    setLoading(true)
    try {
      const url = `${API}/generate-course?skill=${encodeURIComponent(skill.trim())}&level=${level}&time=${encodeURIComponent(time)}&depth=${encodeURIComponent(depth)}`
      const res = await fetch(url, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) {
        const d = await res.json().catch(() => ({}))
        throw new Error(d.detail || `Server error ${res.status}`)
      }
      onGenerate()
    } catch (e) {
      setError(e.message || 'Something went wrong. Try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-8 py-24 w-full min-h-screen">
      <motion.div {...FADE_UP} className="w-full">
        <div className="mb-10">
          <h1 className="text-4xl font-bold font-display mb-3 leading-tight tracking-tight">Generate a course</h1>
          <p className="text-slate-400 text-base">Describe the skill you want to learn and we'll build a structured path for you.</p>
        </div>

        <div className="space-y-8">
          {/* Skill input */}
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-slate-300">What do you want to learn?</label>
            <input
              placeholder="e.g. Rust, Machine Learning, Guitar, Photography..."
              className="w-full bg-surface border border-border rounded px-4 py-3 text-base text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-blue transition-colors"
              value={skill}
              onChange={(e) => setSkill(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
            />
          </div>

          {/* Level slider */}
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <label className="block text-sm font-semibold text-slate-300">Your current level</label>
              <span className="text-xl font-bold font-display text-blue">{level}/10</span>
            </div>
            <input
              type="range" min="1" max="10"
              className="w-full h-1.5 bg-border rounded-[2px] appearance-none cursor-pointer accent-blue"
              value={level}
              onChange={(e) => setLevel(Number(e.target.value))}
            />
            <div className="flex justify-between text-xs text-slate-600 font-mono">
              <span>Beginner</span>
              <span>Expert</span>
            </div>
          </div>

          {/* Time per week */}
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-slate-300">Time available per week</label>
            <div className="grid grid-cols-3 gap-2">
              {TIME_OPTIONS.map(t => (
                <button
                  key={t}
                  onClick={() => setTime(t)}
                  className={`py-2.5 px-3 text-sm border rounded transition-all ${
                    time === t
                      ? 'border-blue bg-blue/10 text-blue font-semibold'
                      : 'border-border text-slate-400 hover:border-slate-500'
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* Course depth */}
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-slate-300">Course depth</label>
            <div className="grid grid-cols-3 gap-2">
              {DEPTH_OPTIONS.map(d => (
                <button
                  key={d.value}
                  onClick={() => setDepth(d.value)}
                  className={`py-3 px-3 text-left border rounded transition-all ${
                    depth === d.value
                      ? 'border-blue bg-blue/10'
                      : 'border-border hover:border-slate-500'
                  }`}
                >
                  <div className={`text-sm font-semibold ${ depth === d.value ? 'text-blue' : 'text-slate-300' }`}>{d.label}</div>
                  <div className="text-xs text-slate-500 mt-0.5">{d.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {error && <p className="text-sm text-rose-400 bg-rose-500/10 border border-rose-500/20 rounded px-4 py-3">{error}</p>}

          <button
            disabled={!skill.trim() || loading}
            onClick={handleGenerate}
            className="w-full py-4 text-base font-bold bg-cyan text-base rounded-[2px] hover:shadow-blue-glow hover:scale-[1.02] active:scale-[0.98] transition-all duration-300 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {loading ? 'Building your path...' : 'Generate my path'}
          </button>
        </div>
      </motion.div>
    </div>
  )
}

async function fetchCourses(token) {
  try {
    const res = await fetch(`${API}/courses`, { headers: { Authorization: `Bearer ${token}` } })
    if (!res.ok) return []
    const list = await res.json()
    const detailed = await Promise.all(list.map(async c => {
      try {
        const r = await fetch(`${API}/courses/${c.id}`, { headers: { Authorization: `Bearer ${token}` } })
        if (!r.ok) return { ...c, modules: [] }
        const d = await r.json()
        return { ...d.course, modules: d.modules || [] }
      } catch { return { ...c, modules: [] } }
    }))
    return detailed
  } catch { return [] }
}

export default function App() {
  const [user, setUser] = useState(null)
  const [page, setPage] = useState('dashboard')
  const [courses, setCourses] = useState([])
  const [selected, setSelected] = useState(null)
  const [showLanding, setShowLanding] = useState(true)
  const [prefilledSkill, setPrefilledSkill] = useState('')

  useEffect(() => {
    const token = localStorage.getItem('op_token')
    if (token && !user) {
      fetch(`${API}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
        .then(r => r.ok ? r.json() : null)
        .then(async data => {
          if (data) {
            const userData = { username: data.username, user_id: data.id, token }
            setUser(userData)
            setShowLanding(false)
            const userCourses = await fetchCourses(token)
            setCourses(userCourses)
          } else {
            localStorage.removeItem('op_token')
          }
        })
        .catch(() => localStorage.removeItem('op_token'))
    }
  }, [])

  const login = async userData => {
    setUser(userData)
    setPage('dashboard')
    const userCourses = await fetchCourses(userData.token)
    setCourses(userCourses)
  }

  const logout = () => {
    setUser(null); setCourses([]); setSelected(null); setPage('dashboard')
    localStorage.removeItem('op_token')
  }

  const refreshCourses = async () => {
    if (!user?.token) return
    const userCourses = await fetchCourses(user.token)
    setCourses(userCourses)
  }

  const completeModule = async (modId, type) => {
    setCourses(prev => prev.map(c => ({
      ...c,
      modules: c.modules.map(m => m.id !== modId ? m : { ...m, is_completed: true, is_skipped: type === 'skipped' })
    })))
    if (selected) {
      setSelected(prev => ({
        ...prev,
        modules: prev.modules.map(m => m.id !== modId ? m : { ...m, is_completed: true, is_skipped: type === 'skipped' })
      }))
    }
    try {
      if (type === 'skipped') {
        await fetch(`${API}/submit-quiz?module_id=${modId}&score=5`, {
          method: 'POST', headers: { Authorization: `Bearer ${user.token}` }
        })
      } else {
        await fetch(`${API}/modules/${modId}/complete`, {
          method: 'POST', headers: { Authorization: `Bearer ${user.token}` }
        })
      }
    } catch (e) { console.error(e) }
  }

  const saveNotes = async (modId, text) => {
    try {
      await fetch(`${API}/modules/${modId}/notes`, {
        method: 'PATCH', headers: { Authorization: `Bearer ${user.token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ notes: text }),
      })
    } catch (e) { console.error(e) }
  }

  if (showLanding) return <LandingPage onGetStarted={() => setShowLanding(false)} />
  if (!user) return <AuthScreen onLogin={login} />

  return (
    <div className="min-h-screen bg-base flex flex-col font-sans text-slate-200 relative">
      <AmbientBackground />
      <NavPill active={page} setPage={setPage} user={user} onLogout={logout} />
      
      <main className="flex-1 overflow-x-hidden flex flex-col relative z-10">
        <div className="fixed inset-0 pointer-events-none">
          <div className="absolute inset-x-0 top-0 h-px bg-cyan/20" />
          <div className="absolute inset-y-0 left-0 w-px bg-cyan/10" />
        </div>
        
        <AnimatePresence mode="wait">
          <motion.div
            key={page}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="flex-1 flex flex-col relative z-10"
          >
            {page === 'dashboard' && <Dashboard courses={courses} onSelectCourse={(c) => { setSelected(c); setPage('course') }} user={user} />}
            {page === 'course' && selected && (
              <CourseView 
                course={selected} 
                onBack={() => setPage('dashboard')} 
                onComplete={completeModule} 
                onSaveNotes={saveNotes}
                token={user.token}
              />
            )}
            {page === 'discover' && <DiscoverPage token={user.token} onEnroll={async () => { await refreshCourses(); setPage('dashboard') }} />}
            {page === 'generate' && <GeneratePage key={prefilledSkill} token={user.token} initialSkill={prefilledSkill} onGenerate={() => { refreshCourses(); setPage('dashboard'); setPrefilledSkill(''); }} />}
            {page === 'career' && <CareerHub token={user.token} onGenerateClick={(skill) => { setPrefilledSkill(skill); setPage('generate'); }} />}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  )
}

