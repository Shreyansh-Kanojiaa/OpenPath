import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'

// ─── DESIGN TOKENS ───────────────────────────────────────────────────────────
// Base: #13141c  Surface: #1e2030  Border: #2e3350  Accent: #7aa2f7
// ─────────────────────────────────────────────────────────────────────────────

// ─── ICONS ───────────────────────────────────────────────────────────────────
const Ico = ({ d, children, className = 'w-5 h-5', viewBox = '0 0 24 24' }) => (
  <svg viewBox={viewBox} fill="none" stroke="currentColor" strokeWidth="1.5"
    strokeLinecap="round" strokeLinejoin="round" className={className}>
    {d ? <path d={d} /> : children}
  </svg>
)

const IcoBrain = () => (
  <Ico className="w-6 h-6">
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.46 2.5 2.5 0 0 1-1.07-4.65A4.5 4.5 0 0 1 3 10.5a4.5 4.5 0 0 1 6-4.24" />
    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.46 2.5 2.5 0 0 0 1.07-4.65A4.5 4.5 0 0 0 21 10.5a4.5 4.5 0 0 0-6-4.24" />
  </Ico>
)
const IcoZap = () => (
  <Ico className="w-6 h-6">
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
  </Ico>
)
const IcoCards = () => (
  <Ico className="w-6 h-6">
    <rect x="2" y="6" width="20" height="13" rx="2" />
    <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
    <line x1="12" y1="11" x2="12" y2="15" />
    <line x1="10" y1="13" x2="14" y2="13" />
  </Ico>
)
const IcoStore = () => (
  <Ico className="w-6 h-6">
    <path d="M3 9l1-5h16l1 5" />
    <path d="M3 9a2 2 0 0 0 2 2 2 2 0 0 0 2-2 2 2 0 0 0 2 2 2 2 0 0 0 2-2 2 2 0 0 0 2 2 2 2 0 0 0 2-2" />
    <path d="M5 20h14a1 1 0 0 0 1-1v-7H4v7a1 1 0 0 0 1 1z" />
  </Ico>
)
const IcoCheck = () => (
  <Ico className="w-4 h-4">
    <polyline points="20 6 9 17 4 12" />
  </Ico>
)
const IcoYT = () => (
  <Ico className="w-5 h-5" viewBox="0 0 24 24">
    <rect x="2" y="5" width="20" height="14" rx="3" fill="rgba(122, 162, 247,0.15)" stroke="#7aa2f7" strokeWidth="1.5" />
    <polygon points="10,9 16,12 10,15" fill="#7aa2f7" stroke="none" />
  </Ico>
)
const IcoArrow = () => (
  <Ico className="w-4 h-4">
    <line x1="5" y1="12" x2="19" y2="12" />
    <polyline points="12 5 19 12 12 19" />
  </Ico>
)

// ─── ANIMATION VARIANTS ───────────────────────────────────────────────────────
const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 28 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.55, delay, ease: [0.16, 1, 0.3, 1] },
})

const inViewFadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 32 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: '-60px' },
  transition: { duration: 0.55, delay, ease: [0.16, 1, 0.3, 1] },
})

// ─── NOISE TEXTURE (SVG Data URI) ────────────────────────────────────────────
const NOISE_SVG = `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.045'/%3E%3C/svg%3E")`

// ─── HERO CARD MOCKUP ─────────────────────────────────────────────────────────
function HeroCard() {
  const modules = [
    { title: 'Foundations & Setup', dur: '18 min', done: true },
    { title: 'Core Concepts Deep Dive', dur: '24 min', done: false },
    { title: 'Building Real Projects', dur: '31 min', done: false },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, x: 60, rotate: 3 }}
      animate={{ opacity: 1, x: 0, rotate: 0 }}
      transition={{ duration: 0.9, delay: 0.6, ease: [0.16, 1, 0.3, 1] }}
      style={{
        background: '#1e2030',
        border: '1px solid #2e3350',
        borderRadius: 8,
        padding: '28px',
        width: '360px',
        flexShrink: 0,
      }}
    >
      {/* Card header */}
      <div style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
          <div style={{
            background: 'rgba(122, 162, 247,0.12)',
            border: '1px solid rgba(122, 162, 247,0.25)',
            borderRadius: 8,
            padding: '4px 10px',
            fontSize: 11,
            fontFamily: 'inherit',
            color: '#7aa2f7',
            letterSpacing: '0.08em',
          }}>
            Beginner
          </div>
          <div style={{
            background: 'rgba(122, 162, 247,0.12)',
            border: '1px solid rgba(122, 162, 247,0.25)',
            borderRadius: 8,
            padding: '4px 10px',
            fontSize: 11,
            fontFamily: 'inherit',
            color: '#7aa2f7',
            letterSpacing: '0.08em',
          }}>
            5 hrs/week
          </div>
        </div>
        <div style={{ fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 22, color: '#e0e4f0', letterSpacing: '-0.02em' }}>
          Rust Programming
        </div>
        <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 12, color: '#8891ad', marginTop: 4 }}>
          8 modules · Custom syllabus
        </div>
      </div>

      {/* Divider */}
      <div style={{ height: 1, background: '#2e3350', marginBottom: 16 }} />

      {/* Module rows */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {modules.map((m, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.9 + i * 0.1, duration: 0.4, ease: 'easeOut' }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              padding: '10px 12px',
              borderRadius: 8,
              background: m.done ? 'rgba(122, 162, 247,0.06)' : 'rgba(255,255,255,0.03)',
              border: `1px solid ${m.done ? 'rgba(122, 162, 247,0.2)' : '#2e3350'}`,
            }}
          >
            {/* YT thumbnail placeholder */}
            <div style={{
              width: 44,
              height: 30,
              borderRadius: 8,
              background: 'rgba(122, 162, 247,0.08)',
              border: '1px solid rgba(122, 162, 247,0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}>
              <IcoYT />
            </div>

            {/* Title + duration */}
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 12,
                fontWeight: 500,
                color: m.done ? '#8891ad' : '#e0e4f0',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                textDecoration: m.done ? 'line-through' : 'none',
              }}>
                {m.title}
              </div>
              <div style={{
                fontFamily: 'inherit',
                fontSize: 10,
                color: '#6b6860',
                marginTop: 2,
              }}>
                {m.dur}
              </div>
            </div>

            {/* Completion chip */}
            {m.done ? (
              <div style={{
                width: 20,
                height: 20,
                borderRadius: 8,
                background: 'rgba(122, 162, 247,0.2)',
                border: '1px solid rgba(122, 162, 247,0.4)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#7aa2f7',
                flexShrink: 0,
              }}>
                <IcoCheck />
              </div>
            ) : (
              <div style={{
                fontFamily: 'inherit',
                fontSize: 10,
                color: '#6b6860',
                flexShrink: 0,
              }}>
                {i === 1 ? '▶' : '○'}
              </div>
            )}
          </motion.div>
        ))}
      </div>

      <div style={{ marginTop: 18 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
          <span style={{ fontFamily: 'inherit', fontSize: 10, color: '#6b6860' }}>Progress</span>
          <span style={{ fontFamily: 'inherit', fontSize: 10, color: '#7aa2f7' }}>12%</span>
        </div>
        <div style={{ height: 3, background: '#2a2f42', borderRadius: 8 }}>
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: '12%' }}
            transition={{ delay: 1.4, duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            style={{ height: '100%', background: '#7aa2f7', borderRadius: 8 }}
          />
        </div>
      </div>
    </motion.div>
  )
}

// ─── HOW IT WORKS CONNECTING LINE ─────────────────────────────────────────────
function ConnectingLine({ inView }) {
  return (
    <div style={{ position: 'relative', height: 2, flex: 1, minWidth: 32 }}>
      <svg width="100%" height="2" style={{ overflow: 'visible' }}>
        <motion.line
          x1="0%" y1="1" x2="100%" y2="1"
          stroke="#2e3350"
          strokeWidth="1.5"
          strokeDasharray="4 4"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={inView ? { pathLength: 1, opacity: 1 } : { pathLength: 0, opacity: 0 }}
          transition={{ duration: 0.8, ease: 'easeInOut', delay: 0.3 }}
        />
      </svg>
    </div>
  )
}

// ─── HOW IT WORKS SECTION ─────────────────────────────────────────────────────
const STEPS = [
  {
    num: '01',
    label: 'Tell OpenPath',
    desc: 'Enter the skill you want to learn, your current level, and your weekly time budget.',
  },
  {
    num: '02',
    label: 'Your syllabus is built',
    desc: 'A structured module-by-module curriculum is generated with curated YouTube videos for each topic.',
  },
  {
    num: '03',
    label: 'Watch, quiz, and accelerate',
    desc: 'Take AI quizzes to skip modules you already know. Use flashcards to lock in what matters.',
  },
]

function HowItWorks() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-80px' })

  return (
    <section style={{ padding: '120px 0', maxWidth: 1200, margin: '0 auto', paddingLeft: 32, paddingRight: 32 }}>
      <motion.div {...inViewFadeUp(0)} style={{ marginBottom: 64 }}>
        <div style={{
          fontFamily: 'inherit',
          fontSize: 11,
          color: '#7aa2f7',
          letterSpacing: '0.04em',
          fontVariant: 'all-small-caps',
          marginBottom: 16,
        }}>
          How it works
        </div>
        <h2 style={{
          fontFamily: 'Inter, sans-serif',
          fontSize: 'clamp(32px, 5vw, 48px)',
          fontWeight: 700,
          color: '#e0e4f0',
          letterSpacing: '-0.03em',
          margin: 0,
        }}>
          Three steps to your first path.
        </h2>
      </motion.div>

      <div ref={ref} style={{ display: 'flex', alignItems: 'flex-start', gap: 0 }}>
        {STEPS.map((step, i) => (
          <div key={step.num} style={{ display: 'contents' }}>
            <motion.div
              initial={{ opacity: 0, y: 32 }}
              animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 32 }}
              transition={{ duration: 0.5, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] }}
              style={{
                background: '#1e2030',
                border: '1px solid #2e3350',
                borderRadius: 8,
                padding: '28px 24px',
                flex: 1,
                minWidth: 0,
              }}
            >
              <div style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 56,
                fontWeight: 800,
                color: '#2e3350',
                lineHeight: 1,
                marginBottom: 16,
                letterSpacing: '-0.04em',
              }}>
                {step.num}
              </div>
              <div style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 16,
                fontWeight: 600,
                color: '#e0e4f0',
                marginBottom: 10,
                letterSpacing: '-0.01em',
              }}>
                {step.label}
              </div>
              <div style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 13,
                color: '#8891ad',
                lineHeight: 1.65,
              }}>
                {step.desc}
              </div>
            </motion.div>

            {i < STEPS.length - 1 && (
              <div key={`line-${i}`} style={{ padding: '52px 16px 0', flexShrink: 0, width: 64 }}>
                <ConnectingLine inView={inView} />
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  )
}

// ─── FEATURES GRID ────────────────────────────────────────────────────────────
const FEATURES = [
  {
    icon: <IcoBrain />,
    name: 'AI Syllabus Generation',
    desc: 'OpenPath breaks down any skill into a structured, ordered module plan tailored to your level and goals.',
  },
  {
    icon: <IcoZap />,
    name: 'Quiz-to-Skip Modules',
    desc: 'Already know the basics? Pass a short AI-generated quiz and skip straight to what challenges you.',
  },
  {
    icon: <IcoCards />,
    name: 'AI Flashcards',
    desc: 'Key concepts from each module are automatically distilled into spaced-repetition flashcards.',
  },
  {
    icon: <IcoStore />,
    name: 'Community Marketplace',
    desc: 'Browse and clone learning paths built by other users. Share yours to help others get started faster.',
  },
]

function FeatureGrid() {
  return (
    <section style={{ padding: '120px 0', maxWidth: 1200, margin: '0 auto', paddingLeft: 32, paddingRight: 32 }}>
      <motion.div {...inViewFadeUp(0)} style={{ marginBottom: 64 }}>
        <div style={{
          fontFamily: 'inherit',
          fontSize: 11,
          color: '#7aa2f7',
          letterSpacing: '0.04em',
          fontVariant: 'all-small-caps',
          marginBottom: 16,
        }}>
          Features
        </div>
        <h2 style={{
          fontFamily: 'Inter, sans-serif',
          fontSize: 'clamp(32px, 5vw, 48px)',
          fontWeight: 700,
          color: '#e0e4f0',
          letterSpacing: '-0.03em',
          margin: 0,
        }}>
          Everything you need to go deep.
        </h2>
      </motion.div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: 16,
      }}>
        {FEATURES.map((f, i) => (
          <motion.div
            key={f.name}
            initial={{ opacity: 0, y: 28 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-40px' }}
            transition={{ duration: 0.5, delay: i * 0.06, ease: [0.16, 1, 0.3, 1] }}
            style={{
              background: '#1e2030',
              border: '1px solid #2e3350',
              borderRadius: 8,
              padding: '32px',
              transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
            }}
            whileHover={{ borderColor: '#3d3b36' }}
          >
            <div style={{
              width: 44,
              height: 44,
              borderRadius: 8,
              background: 'rgba(122, 162, 247,0.08)',
              border: '1px solid rgba(122, 162, 247,0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#7aa2f7',
              marginBottom: 20,
            }}>
              {f.icon}
            </div>
            <div style={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 17,
              fontWeight: 600,
              color: '#e0e4f0',
              letterSpacing: '-0.01em',
              marginBottom: 10,
            }}>
              {f.name}
            </div>
            <div style={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 13,
              color: '#8891ad',
              lineHeight: 1.65,
            }}>
              {f.desc}
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  )
}

// ─── COMMUNITY SECTION ────────────────────────────────────────────────────────
const COMMUNITY_PATHS = [
  { skill: 'Advanced Rust Systems', user: '@oxide_core', modules: 12, time: '6 hrs/week' },
  { skill: 'Generative AI Design', user: '@neural_flow', modules: 8, time: '4 hrs/week' },
  { skill: 'Orbital Mechanics', user: '@spacewalk', modules: 15, time: '8 hrs/week' },
]

function CommunitySection() {
  return (
    <section style={{ padding: '120px 0', maxWidth: 1200, margin: '0 auto', paddingLeft: 32, paddingRight: 32 }}>
      <motion.div {...inViewFadeUp(0)} style={{ marginBottom: 56 }}>
        <div style={{
          fontFamily: 'inherit',
          fontSize: 11,
          color: '#7aa2f7',
          letterSpacing: '0.04em',
          fontVariant: 'all-small-caps',
          marginBottom: 16,
        }}>
          Community
        </div>
        <h2 style={{
          fontFamily: 'Inter, sans-serif',
          fontSize: 'clamp(32px, 5vw, 48px)',
          fontWeight: 700,
          color: '#e0e4f0',
          letterSpacing: '-0.03em',
          margin: 0,
        }}>
          Paths shared by the community.
        </h2>
      </motion.div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
        {COMMUNITY_PATHS.map((p, i) => (
          <motion.div
            key={p.skill}
            initial={{ opacity: 0, y: 32 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-40px' }}
            transition={{ duration: 0.5, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] }}
            style={{
              background: '#1e2030',
              border: '1px solid #2e3350',
              borderLeft: '1px solid #7aa2f7',
              borderRadius: 8,
              padding: '28px 24px',
              cursor: 'pointer',
              transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
            }}
            whileHover={{ borderLeftColor: '#d4b96a' }}
          >
            <div style={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 18,
              fontWeight: 700,
              color: '#e0e4f0',
              letterSpacing: '-0.02em',
              marginBottom: 8,
              lineHeight: 1.3,
            }}>
              {p.skill}
            </div>
            <div style={{
              fontFamily: 'inherit',
              fontSize: 11,
              color: '#7aa2f7',
              marginBottom: 20,
            }}>
              {p.user}
            </div>
            <div style={{ display: 'flex', gap: 16 }}>
              <div style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 12,
                color: '#8891ad',
                display: 'flex',
                alignItems: 'center',
                gap: 5,
              }}>
                <span style={{ color: '#6b6860' }}>◈</span> {p.modules} modules
              </div>
              <div style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 12,
                color: '#8891ad',
                display: 'flex',
                alignItems: 'center',
                gap: 5,
              }}>
                <span style={{ color: '#6b6860' }}>◷</span> {p.time}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  )
}

// ─── FOOTER CTA ───────────────────────────────────────────────────────────────
function FooterCTA({ onGetStarted }) {
  return (
    <section style={{
      background: '#1e2030',
      borderTop: '1px solid #2e3350',
      padding: '120px 32px',
      textAlign: 'center',
    }}>
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: '-60px' }}
        transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
        style={{ maxWidth: 600, margin: '0 auto' }}
      >
        <h2 style={{
          fontFamily: 'Inter, sans-serif',
          fontSize: 'clamp(36px, 6vw, 64px)',
          fontWeight: 800,
          color: '#e0e4f0',
          letterSpacing: '-0.04em',
          lineHeight: 1.1,
          marginBottom: 40,
        }}>
          Start your first path free.
        </h2>
        <button
          onClick={onGetStarted}
          id="footer-cta-btn"
          style={{
            background: '#7aa2f7',
            color: '#13141c',
            fontFamily: 'Inter, sans-serif',
            fontWeight: 700,
            fontSize: 16,
            letterSpacing: '-0.01em',
            border: 'none',
            borderRadius: 8,
            padding: '16px 40px',
            cursor: 'pointer',
            transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
          }}
          onMouseEnter={e => { e.target.style.background = '#d4b96a' }}
          onMouseLeave={e => { e.target.style.background = '#7aa2f7' }}
        >
          Generate My Path <IcoArrow />
        </button>
      </motion.div>
    </section>
  )
}

// ─── NAV ──────────────────────────────────────────────────────────────────────
function LandingNav({ onGetStarted }) {
  return (
    <motion.nav
      initial={{ opacity: 0, y: -16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      style={{
        position: 'fixed',
        top: 0, left: 0, right: 0,
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '18px 32px',
        background: '#1e2030',
        borderBottom: '1px solid #2e3350',
      }}
    >
      {/* Logo */}
      <div style={{
        fontFamily: 'Inter, sans-serif',
        fontWeight: 800,
        fontSize: 20,
        color: '#e0e4f0',
        letterSpacing: '-0.03em',
        display: 'flex',
        alignItems: 'center',
        gap: 8,
      }}>
        <span style={{
          display: 'inline-block',
          width: 28,
          height: 28,
          borderRadius: 8,
          background: '#7aa2f7',
          color: '#13141c',
          fontFamily: 'Inter, sans-serif',
          fontWeight: 800,
          fontSize: 16,
          textAlign: 'center',
          lineHeight: '28px',
        }}>O</span>
        OpenPath
      </div>

      {/* Right side */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <button
          onClick={onGetStarted}
          style={{
            background: 'transparent',
            color: '#8891ad',
            border: 'none',
            fontFamily: 'Inter, sans-serif',
            fontSize: 14,
            cursor: 'pointer',
            padding: '8px 16px',
            transition: 'color 0.2s ease',
          }}
          onMouseEnter={e => { e.target.style.color = '#e0e4f0' }}
          onMouseLeave={e => { e.target.style.color = '#8891ad' }}
        >
          Sign in
        </button>
        <button
          onClick={onGetStarted}
          id="nav-cta-btn"
          style={{
            background: '#7aa2f7',
            color: '#13141c',
            border: 'none',
            borderRadius: 8,
            fontFamily: 'Inter, sans-serif',
            fontWeight: 600,
            fontSize: 14,
            padding: '9px 22px',
            cursor: 'pointer',
            transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
          }}
          onMouseEnter={e => { e.target.style.background = '#d4b96a' }}
          onMouseLeave={e => { e.target.style.background = '#7aa2f7' }}
        >
          Get started free
        </button>
      </div>
    </motion.nav>
  )
}

// ─── HERO SECTION ─────────────────────────────────────────────────────────────
const HEADLINE_WORDS_1 = ['Learn', 'anything.']
const HEADLINE_WORDS_2 = ['Follow', 'the', 'path.']

function Hero({ onGetStarted }) {
  return (
    <section style={{
      position: 'relative',
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      paddingTop: 96,
      paddingBottom: 80,
      overflow: 'hidden',
      maxWidth: 1200,
      margin: '0 auto',
      padding: '160px 32px 80px',
    }}>
      {/* Left: text + CTA */}
      <div style={{ flex: 1, minWidth: 0, paddingRight: 48 }}>
        {/* Eyebrow */}
        <motion.div
          {...fadeUp(0.1)}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
            background: 'rgba(122, 162, 247,0.08)',
            border: '1px solid rgba(122, 162, 247,0.2)',
            borderRadius: 8,
            padding: '6px 16px 6px 10px',
            marginBottom: 40,
          }}
        >
          <span style={{
            fontFamily: 'inherit',
            fontSize: 12,
            color: '#8891ad',
            fontVariant: 'all-small-caps',
            letterSpacing: '0.06em',
          }}>
            Free and open source
          </span>
        </motion.div>

        {/* Headline line 1 */}
        <h1 style={{
          fontFamily: 'Inter, sans-serif',
          fontWeight: 800,
          fontSize: 'clamp(52px, 7vw, 88px)',
          letterSpacing: '-0.04em',
          lineHeight: 1.0,
          color: '#e0e4f0',
          margin: 0,
        }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0 14px', marginBottom: 4 }}>
            {HEADLINE_WORDS_1.map((word, i) => (
              <motion.span
                key={word}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + i * 0.08, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                style={{ display: 'inline-block' }}
              >
                {word}
              </motion.span>
            ))}
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0 14px' }}>
            {HEADLINE_WORDS_2.map((word, i) => (
              <motion.span
                key={word}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.36 + i * 0.08, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                style={{
                  display: 'inline-block',
                  color: word === 'the' || word === 'path.' ? '#7aa2f7' : '#e0e4f0',
                }}
              >
                {word}
              </motion.span>
            ))}
          </div>
        </h1>

        {/* Sub-headline */}
        <motion.p
          {...fadeUp(0.65)}
          style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 'clamp(15px, 2vw, 18px)',
            color: '#8891ad',
            lineHeight: 1.7,
            maxWidth: 480,
            margin: '28px 0 44px',
          }}
        >
          OpenPath uses AI to build you a structured, video-backed learning track
          for any skill — in minutes.
        </motion.p>

        {/* CTA */}
        <motion.div {...fadeUp(0.78)} style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
          <button
            onClick={onGetStarted}
            id="hero-cta-btn"
            style={{
              background: '#7aa2f7',
              color: '#13141c',
              border: 'none',
              borderRadius: 8,
              fontFamily: 'Inter, sans-serif',
              fontWeight: 700,
              fontSize: 16,
              letterSpacing: '-0.01em',
              padding: '16px 36px',
              cursor: 'pointer',
              transition: 'all 0.25s ease',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
            }}
            onMouseEnter={e => { e.currentTarget.style.background = '#d4b96a' }}
            onMouseLeave={e => { e.currentTarget.style.background = '#7aa2f7' }}
          >
            Generate my path <IcoArrow />
          </button>
          <span style={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#6b6860' }}>
            Free to start · No card required
          </span>
        </motion.div>
      </div>

      {/* Right: card mockup */}
      <div style={{ flexShrink: 0, display: 'flex', alignItems: 'center' }}>
        <HeroCard />
      </div>
    </section>
  )
}

// ─── NOISE OVERLAY ────────────────────────────────────────────────────────────
function NoiseHero() {
  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      backgroundImage: NOISE_SVG,
      backgroundRepeat: 'repeat',
      backgroundSize: '200px 200px',
      pointerEvents: 'none',
      zIndex: 0,
    }} />
  )
}

// ─── MAIN LANDING PAGE ────────────────────────────────────────────────────────
export default function LandingPage({ onGetStarted }) {
  return (
    <div style={{
      minHeight: '100vh',
      background: '#13141c',
      color: '#e0e4f0',
      overflowX: 'hidden',
    }}>
      <style>{`
        @media (max-width: 768px) {
          .landing-hero-flex { flex-direction: column !important; }
          .landing-hero-card { display: none !important; }
          .landing-feature-grid { grid-template-columns: 1fr !important; }
          .landing-community-grid { grid-template-columns: 1fr !important; }
          .landing-steps-flex { flex-direction: column !important; gap: 16px !important; }
          .landing-steps-line { display: none !important; }
        }
      `}</style>

      <LandingNav onGetStarted={onGetStarted} />

      <div style={{ position: 'relative' }}>
        <div style={{ position: 'relative', zIndex: 1 }}>
          <div
            className="landing-hero-flex"
            style={{
              maxWidth: 1200,
              margin: '0 auto',
              padding: '160px 32px 80px',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            {/* Left: text + CTA */}
            <div style={{ flex: 1, minWidth: 0, paddingRight: 48 }}>
              <motion.div
                {...fadeUp(0.1)}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                  background: 'rgba(122, 162, 247,0.08)',
                  border: '1px solid rgba(122, 162, 247,0.2)',
                  borderRadius: 8,
                  padding: '6px 16px 6px 10px',
                  marginBottom: 40,
                }}
              >
                <span style={{
                  fontFamily: 'inherit',
                  fontSize: 12,
                  color: '#8891ad',
                  fontVariant: 'all-small-caps',
                  letterSpacing: '0.06em',
                }}>
                  Free and open source
                </span>
              </motion.div>

              <h1 style={{
                fontFamily: 'Inter, sans-serif',
                fontWeight: 800,
                fontSize: 'clamp(52px, 6.5vw, 88px)',
                letterSpacing: '-0.04em',
                lineHeight: 1.0,
                color: '#e0e4f0',
                margin: 0,
              }}>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0 14px', marginBottom: 4 }}>
                  {HEADLINE_WORDS_1.map((word, i) => (
                    <motion.span
                      key={word + i}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.2 + i * 0.08, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                      style={{ display: 'inline-block' }}
                    >
                      {word}
                    </motion.span>
                  ))}
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0 14px' }}>
                  {HEADLINE_WORDS_2.map((word, i) => (
                    <motion.span
                      key={word + i}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.36 + i * 0.08, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                      style={{
                        display: 'inline-block',
                        color: i > 0 ? '#7aa2f7' : '#e0e4f0',
                      }}
                    >
                      {word}
                    </motion.span>
                  ))}
                </div>
              </h1>

              <motion.p
                {...fadeUp(0.65)}
                style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 'clamp(15px, 1.8vw, 18px)',
                  color: '#8891ad',
                  lineHeight: 1.7,
                  maxWidth: 480,
                  margin: '28px 0 44px',
                }}
              >
                OpenPath uses AI to build you a structured, video-backed learning track
                for any skill — in minutes.
              </motion.p>

              <motion.div {...fadeUp(0.78)} style={{ display: 'flex', alignItems: 'center', gap: 20, flexWrap: 'wrap' }}>
                <button
                  onClick={onGetStarted}
                  id="hero-cta-btn"
                  style={{
                    background: '#7aa2f7',
                    color: '#13141c',
                    border: 'none',
                    borderRadius: 8,
                    fontFamily: 'Inter, sans-serif',
                    fontWeight: 700,
                    fontSize: 16,
                    letterSpacing: '-0.01em',
                    padding: '16px 36px',
                    cursor: 'pointer',
                    transition: 'all 0.25s ease',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 8,
                  }}
                  onMouseEnter={e => { e.currentTarget.style.background = '#d4b96a' }}
                  onMouseLeave={e => { e.currentTarget.style.background = '#7aa2f7' }}
                >
                  Generate my path →
                </button>
                <span style={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#6b6860' }}>
                  Free to start · No card required
                </span>
              </motion.div>
            </div>

            {/* Right: hero card */}
            <div className="landing-hero-card" style={{ flexShrink: 0 }}>
              <HeroCard />
            </div>
          </div>
        </div>

        {/* subtle bottom fade into content */}
        <div style={{
          position: 'absolute',
          bottom: 0, left: 0, right: 0,
          height: 120,
          background: '#13141c',
          pointerEvents: 'none',
        }} />
      </div>

      {/* Divider line */}
      <div style={{ height: 1, background: '#2e3350', maxWidth: 1200, margin: '0 auto 0', marginLeft: 32, marginRight: 32 }} />

      {/* How It Works */}
      <HowItWorks />

      {/* Divider */}
      <div style={{ height: 1, background: '#2e3350', maxWidth: 1200, margin: '0 32px' }} />

      {/* Feature Grid */}
      <FeatureGrid />

      {/* Divider */}
      <div style={{ height: 1, background: '#2e3350', maxWidth: 1200, margin: '0 32px' }} />

      {/* Community */}
      <CommunitySection />

      {/* Footer CTA */}
      <FooterCTA onGetStarted={onGetStarted} />
    </div>
  )
}
