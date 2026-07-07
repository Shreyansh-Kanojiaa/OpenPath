import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import DotGrid from './components/DotGrid'

// ─── DESIGN TOKENS ───────────────────────────────────────────────────────────
// Base: #04050a  Surface: #0a0e11  Border: #1c2326  Accent: #86c4bb
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

// ─── HERO CARD MOCKUP ─────────────────────────────────────────────────────────
function HeroCard() {
  const modules = [
    { title: 'JavaScript refresher', meta: '3 lessons · 26 min', state: 'done' },
    { title: 'Components & JSX', meta: '4 lessons · 38 min', state: 'done' },
    { title: 'State & props', meta: 'In progress · lesson 2 of 5', state: 'active', pct: 40 },
    { title: 'Hooks in depth', meta: 'Locked', state: 'locked', num: 4 },
  ]

  return (
    <div style={{ position: 'relative', width: 360, flexShrink: 0 }}>
      {/* Ghost card peeking out from behind for a stacked-deck effect */}
      <motion.div
        initial={{ opacity: 0, rotate: 8, x: 70, y: 10 }}
        animate={{ opacity: 1, rotate: 6, x: 22, y: 14 }}
        transition={{ duration: 0.9, delay: 0.5, ease: [0.16, 1, 0.3, 1] }}
        style={{
          position: 'absolute', inset: 0,
          background: '#0a0e11',
          border: '1px solid #1c2326',
          borderRadius: 20,
          zIndex: 0,
        }}
      />

      <motion.div
        initial={{ opacity: 0, rotate: 3, x: 60 }}
        animate={{ opacity: 1, rotate: -2, x: 0 }}
        transition={{ duration: 0.9, delay: 0.65, ease: [0.16, 1, 0.3, 1] }}
        style={{
          position: 'relative', zIndex: 1,
          background: '#0a0e11',
          border: '1px solid #1c2326',
          borderRadius: 20,
          padding: '26px',
          boxShadow: '0 30px 60px -20px rgba(0,0,0,0.6)',
        }}
      >
        {/* Card header */}
        <div style={{ marginBottom: 18 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: 5,
              background: 'rgba(134, 196, 187,0.12)',
              border: '1px solid rgba(134, 196, 187,0.25)',
              borderRadius: 999,
              padding: '4px 10px',
              fontSize: 10,
              fontFamily: 'JetBrains Mono, monospace',
              color: '#86c4bb',
              letterSpacing: '0.06em',
            }}>
              ★ AI GENERATED
            </div>
            <div style={{
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid #1c2326',
              borderRadius: 999,
              padding: '4px 10px',
              fontSize: 10,
              fontFamily: 'JetBrains Mono, monospace',
              color: '#9298ad',
              letterSpacing: '0.04em',
            }}>
              6 weeks · 24 lessons
            </div>
          </div>
          <div style={{ fontFamily: 'Newsreader, serif', fontWeight: 500, fontSize: 24, color: '#f2f3f9' }}>
            React, from zero
          </div>
          <div style={{ fontFamily: 'Hanken Grotesk, sans-serif', fontSize: 12, color: '#9298ad', marginTop: 4 }}>
            Beginner · 5 hrs / week · tuned to you
          </div>
        </div>

        <div style={{ height: 1, background: '#1c2326', marginBottom: 14 }} />

        {/* Module rows */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {modules.map((m, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.95 + i * 0.1, duration: 0.4, ease: 'easeOut' }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                padding: '10px 12px',
                borderRadius: 12,
                background: m.state === 'active' ? 'rgba(134, 196, 187,0.1)' : 'transparent',
                border: `1px solid ${m.state === 'active' ? 'rgba(134, 196, 187,0.35)' : 'transparent'}`,
              }}
            >
              <div style={{
                width: 22, height: 22, borderRadius: '50%', flexShrink: 0,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: m.state === 'done' ? 'rgba(134, 196, 187,0.18)' : 'transparent',
                border: `1px solid ${m.state === 'done' ? 'rgba(134, 196, 187,0.4)' : m.state === 'active' ? 'rgba(134, 196, 187,0.5)' : '#2c3538'}`,
                color: m.state === 'locked' ? '#71768a' : '#86c4bb',
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: 10,
              }}>
                {m.state === 'done' ? <IcoCheck /> : m.state === 'active' ? <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#86c4bb', display: 'block' }} /> : m.num}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  fontFamily: 'Hanken Grotesk, sans-serif',
                  fontSize: 12.5,
                  fontWeight: 500,
                  color: m.state === 'locked' ? '#71768a' : '#f2f3f9',
                }}>
                  {m.title}
                </div>
                <div style={{ fontFamily: 'inherit', fontSize: 10, color: '#71768a', marginTop: 1 }}>{m.meta}</div>
              </div>
              {m.state === 'active' && (
                <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: '#86c4bb', flexShrink: 0 }}>{m.pct}%</span>
              )}
            </motion.div>
          ))}
        </div>

        <div style={{ height: 1, background: '#1c2326', margin: '14px 0' }} />

        <div style={{
          display: 'flex', alignItems: 'center', gap: 8,
          background: 'rgba(255,255,255,0.03)',
          border: '1px solid #1c2326',
          borderRadius: 999,
          padding: '9px 14px',
        }}>
          <span style={{ fontFamily: 'Hanken Grotesk, sans-serif', fontSize: 11.5, color: '#71768a', flex: 1 }}>Ask the tutor about useEffect…</span>
          <span style={{ color: '#86c4bb' }}><IcoArrow /></span>
        </div>
      </motion.div>
    </div>
  )
}

// ─── HOW IT WORKS CONNECTING LINE ─────────────────────────────────────────────
function ConnectingLine({ inView }) {
  return (
    <div style={{ position: 'relative', height: 2, flex: 1, minWidth: 32 }}>
      <svg width="100%" height="2" style={{ overflow: 'visible' }}>
        <motion.line
          x1="0%" y1="1" x2="100%" y2="1"
          stroke="#1c2326"
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
          color: '#86c4bb',
          letterSpacing: '0.04em',
          fontVariant: 'all-small-caps',
          marginBottom: 16,
        }}>
          How it works
        </div>
        <h2 style={{
          fontFamily: 'Newsreader, serif',
          fontSize: 'clamp(32px, 5vw, 48px)',
          fontWeight: 500,
          color: '#f2f3f9',
          letterSpacing: '-0.01em',
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
                background: '#0a0e11',
                border: '1px solid #1c2326',
                borderRadius: 8,
                padding: '28px 24px',
                flex: 1,
                minWidth: 0,
              }}
            >
              <div style={{
                fontFamily: 'Hanken Grotesk, sans-serif',
                fontSize: 56,
                fontWeight: 800,
                color: '#1c2326',
                lineHeight: 1,
                marginBottom: 16,
                letterSpacing: '-0.04em',
              }}>
                {step.num}
              </div>
              <div style={{
                fontFamily: 'Hanken Grotesk, sans-serif',
                fontSize: 16,
                fontWeight: 600,
                color: '#f2f3f9',
                marginBottom: 10,
                letterSpacing: '-0.01em',
              }}>
                {step.label}
              </div>
              <div style={{
                fontFamily: 'Hanken Grotesk, sans-serif',
                fontSize: 13,
                color: '#9298ad',
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
          color: '#86c4bb',
          letterSpacing: '0.04em',
          fontVariant: 'all-small-caps',
          marginBottom: 16,
        }}>
          Features
        </div>
        <h2 style={{
          fontFamily: 'Newsreader, serif',
          fontSize: 'clamp(32px, 5vw, 48px)',
          fontWeight: 500,
          color: '#f2f3f9',
          letterSpacing: '-0.01em',
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
              background: '#0a0e11',
              border: '1px solid #1c2326',
              borderRadius: 8,
              padding: '32px',
              transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
            }}
            whileHover={{ borderColor: '#2c3538' }}
          >
            <div style={{
              width: 44,
              height: 44,
              borderRadius: 8,
              background: 'rgba(134, 196, 187,0.08)',
              border: '1px solid rgba(134, 196, 187,0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#86c4bb',
              marginBottom: 20,
            }}>
              {f.icon}
            </div>
            <div style={{
              fontFamily: 'Hanken Grotesk, sans-serif',
              fontSize: 17,
              fontWeight: 600,
              color: '#f2f3f9',
              letterSpacing: '-0.01em',
              marginBottom: 10,
            }}>
              {f.name}
            </div>
            <div style={{
              fontFamily: 'Hanken Grotesk, sans-serif',
              fontSize: 13,
              color: '#9298ad',
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
          color: '#86c4bb',
          letterSpacing: '0.04em',
          fontVariant: 'all-small-caps',
          marginBottom: 16,
        }}>
          Community
        </div>
        <h2 style={{
          fontFamily: 'Newsreader, serif',
          fontSize: 'clamp(32px, 5vw, 48px)',
          fontWeight: 500,
          color: '#f2f3f9',
          letterSpacing: '-0.01em',
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
              background: '#0a0e11',
              border: '1px solid #1c2326',
              borderLeft: '1px solid #86c4bb',
              borderRadius: 8,
              padding: '28px 24px',
              cursor: 'pointer',
              transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
            }}
            whileHover={{ borderLeftColor: '#9fcebe' }}
          >
            <div style={{
              fontFamily: 'Hanken Grotesk, sans-serif',
              fontSize: 18,
              fontWeight: 700,
              color: '#f2f3f9',
              letterSpacing: '-0.02em',
              marginBottom: 8,
              lineHeight: 1.3,
            }}>
              {p.skill}
            </div>
            <div style={{
              fontFamily: 'inherit',
              fontSize: 11,
              color: '#86c4bb',
              marginBottom: 20,
            }}>
              {p.user}
            </div>
            <div style={{ display: 'flex', gap: 16 }}>
              <div style={{
                fontFamily: 'Hanken Grotesk, sans-serif',
                fontSize: 12,
                color: '#9298ad',
                display: 'flex',
                alignItems: 'center',
                gap: 5,
              }}>
                <span style={{ color: '#71768a' }}>◈</span> {p.modules} modules
              </div>
              <div style={{
                fontFamily: 'Hanken Grotesk, sans-serif',
                fontSize: 12,
                color: '#9298ad',
                display: 'flex',
                alignItems: 'center',
                gap: 5,
              }}>
                <span style={{ color: '#71768a' }}>◷</span> {p.time}
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
      background: '#0a0e11',
      borderTop: '1px solid #1c2326',
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
          fontFamily: 'Newsreader, serif',
          fontSize: 'clamp(36px, 6vw, 64px)',
          fontWeight: 500,
          color: '#f2f3f9',
          letterSpacing: '-0.01em',
          lineHeight: 1.1,
          marginBottom: 40,
        }}>
          Start your <em style={{ color: '#86c4bb' }}>first path</em> free.
        </h2>
        <button
          onClick={onGetStarted}
          id="footer-cta-btn"
          style={{
            background: '#86c4bb',
            color: '#04050a',
            fontFamily: 'Hanken Grotesk, sans-serif',
            fontWeight: 700,
            fontSize: 16,
            letterSpacing: '-0.01em',
            border: 'none',
            borderRadius: 999,
            padding: '16px 40px',
            cursor: 'pointer',
            transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
          }}
          onMouseEnter={e => { e.target.style.background = '#9fcebe' }}
          onMouseLeave={e => { e.target.style.background = '#86c4bb' }}
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
        background: '#0a0e11',
        borderBottom: '1px solid #1c2326',
      }}
    >
      {/* Logo */}
      <div style={{
        fontFamily: 'Hanken Grotesk, sans-serif',
        fontWeight: 800,
        fontSize: 20,
        color: '#f2f3f9',
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
          background: '#86c4bb',
          color: '#04050a',
          fontFamily: 'Hanken Grotesk, sans-serif',
          fontWeight: 800,
          fontSize: 16,
          textAlign: 'center',
          lineHeight: '28px',
        }}>O</span>
        OpenPath
      </div>

      {/* Center links */}
      <div className="landing-nav-links" style={{ display: 'flex', alignItems: 'center', gap: 32 }}>
        {['How it works', 'Features', 'Community'].map(label => (
          <a
            key={label}
            href="#"
            onClick={e => e.preventDefault()}
            style={{
              fontFamily: 'Hanken Grotesk, sans-serif',
              fontSize: 14,
              color: '#9298ad',
              textDecoration: 'none',
              transition: 'color 0.2s ease',
            }}
            onMouseEnter={e => { e.currentTarget.style.color = '#f2f3f9' }}
            onMouseLeave={e => { e.currentTarget.style.color = '#9298ad' }}
          >
            {label}
          </a>
        ))}
      </div>

      {/* Right side */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <button
          onClick={onGetStarted}
          style={{
            background: 'transparent',
            color: '#9298ad',
            border: 'none',
            fontFamily: 'Hanken Grotesk, sans-serif',
            fontSize: 14,
            cursor: 'pointer',
            padding: '8px 16px',
            transition: 'color 0.2s ease',
          }}
          onMouseEnter={e => { e.target.style.color = '#f2f3f9' }}
          onMouseLeave={e => { e.target.style.color = '#9298ad' }}
        >
          Sign in
        </button>
        <button
          onClick={onGetStarted}
          id="nav-cta-btn"
          style={{
            background: '#86c4bb',
            color: '#04050a',
            border: 'none',
            borderRadius: 999,
            fontFamily: 'Hanken Grotesk, sans-serif',
            fontWeight: 600,
            fontSize: 14,
            padding: '9px 22px',
            cursor: 'pointer',
            transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
          }}
          onMouseEnter={e => { e.target.style.background = '#9fcebe' }}
          onMouseLeave={e => { e.target.style.background = '#86c4bb' }}
        >
          Get started free
        </button>
      </div>
    </motion.nav>
  )
}

// ─── HERO SECTION ─────────────────────────────────────────────────────────────
const HEADLINE_WORDS_1 = ['Skip', 'the', 'rabbit', 'holes.']
const HEADLINE_WORDS_2 = ['Follow', 'one', 'clear', 'path.']

// ─── MAIN LANDING PAGE ────────────────────────────────────────────────────────
export default function LandingPage({ onGetStarted }) {
  return (
    <div style={{
      position: 'relative',
      minHeight: '100vh',
      background: '#04050a',
      color: '#f2f3f9',
      overflowX: 'hidden',
    }}>
      <style>{`
        @media (max-width: 768px) {
          .landing-hero-flex { flex-direction: column !important; }
          .landing-hero-card { display: none !important; }
          .landing-nav-links { display: none !important; }
          .landing-feature-grid { grid-template-columns: 1fr !important; }
          .landing-community-grid { grid-template-columns: 1fr !important; }
          .landing-steps-flex { flex-direction: column !important; gap: 16px !important; }
          .landing-steps-line { display: none !important; }
        }
      `}</style>

      <DotGrid />
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
                  background: 'rgba(134, 196, 187,0.08)',
                  border: '1px solid rgba(134, 196, 187,0.2)',
                  borderRadius: 999,
                  padding: '6px 16px 6px 12px',
                  marginBottom: 40,
                }}
              >
                <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#86c4bb', display: 'inline-block' }} />
                <span style={{
                  fontFamily: 'JetBrains Mono, monospace',
                  fontSize: 11,
                  color: '#9298ad',
                  letterSpacing: '0.1em',
                  textTransform: 'uppercase',
                }}>
                  A curriculum built for you
                </span>
              </motion.div>

              <h1 style={{
                fontFamily: 'Newsreader, serif',
                fontWeight: 400,
                fontSize: 'clamp(46px, 6vw, 76px)',
                letterSpacing: '-0.01em',
                lineHeight: 1.08,
                color: '#f2f3f9',
                margin: 0,
              }}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                >
                  {HEADLINE_WORDS_1.join(' ')}
                </motion.div>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.36, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                  style={{ fontStyle: 'italic', color: '#86c4bb' }}
                >
                  {HEADLINE_WORDS_2.join(' ')}
                </motion.div>
              </h1>

              <motion.p
                {...fadeUp(0.65)}
                style={{
                  fontFamily: 'Hanken Grotesk, sans-serif',
                  fontSize: 'clamp(15px, 1.8vw, 18px)',
                  color: '#9298ad',
                  lineHeight: 1.7,
                  maxWidth: 480,
                  margin: '28px 0 44px',
                }}
              >
                Tell OpenPath the skill, your level, and the hours you can spare.
                It builds a structured, video-backed syllabus — and a tutor that
                knows every lesson by heart.
              </motion.p>

              <motion.div {...fadeUp(0.78)} style={{ display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap' }}>
                <button
                  onClick={onGetStarted}
                  id="hero-cta-btn"
                  style={{
                    background: '#86c4bb',
                    color: '#04050a',
                    border: 'none',
                    borderRadius: 999,
                    fontFamily: 'Hanken Grotesk, sans-serif',
                    fontWeight: 700,
                    fontSize: 15,
                    letterSpacing: '-0.01em',
                    padding: '14px 28px',
                    cursor: 'pointer',
                    transition: 'all 0.25s ease',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 8,
                  }}
                  onMouseEnter={e => { e.currentTarget.style.background = '#9fcebe' }}
                  onMouseLeave={e => { e.currentTarget.style.background = '#86c4bb' }}
                >
                  Build my path — free <IcoArrow />
                </button>
                <button
                  onClick={onGetStarted}
                  style={{
                    background: 'transparent',
                    color: '#f2f3f9',
                    border: '1px solid #1c2326',
                    borderRadius: 999,
                    fontFamily: 'Hanken Grotesk, sans-serif',
                    fontWeight: 600,
                    fontSize: 15,
                    padding: '14px 24px',
                    cursor: 'pointer',
                    transition: 'all 0.25s ease',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 8,
                  }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = '#2c3538' }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = '#1c2326' }}
                >
                  <span style={{ fontSize: 11 }}>▶</span> Watch the 2-min demo
                </button>
              </motion.div>

              <motion.div {...fadeUp(0.85)} style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 32 }}>
                <div style={{ display: 'flex' }}>
                  {['M', 'A', 'J'].map((letter, i) => (
                    <div key={letter} style={{
                      width: 28, height: 28, borderRadius: '50%',
                      background: 'linear-gradient(135deg, rgba(134,196,187,0.35), rgba(134,196,187,0.12))',
                      border: '2px solid #04050a',
                      marginLeft: i === 0 ? 0 : -8,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontFamily: 'Hanken Grotesk, sans-serif', fontSize: 11, fontWeight: 700, color: '#d3e6dc',
                    }}>
                      {letter}
                    </div>
                  ))}
                  <div style={{
                    width: 28, height: 28, borderRadius: '50%',
                    background: '#10151a', border: '2px solid #04050a', marginLeft: -8,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontFamily: 'Hanken Grotesk, sans-serif', fontSize: 11, fontWeight: 700, color: '#9298ad',
                  }}>
                    +
                  </div>
                </div>
                <span style={{ fontFamily: 'Hanken Grotesk, sans-serif', fontSize: 13, color: '#9298ad' }}>
                  Built for learners on a path made just for them
                </span>
              </motion.div>

              {/* Mini feature strip */}
              <motion.div
                {...fadeUp(0.9)}
                style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginTop: 56, maxWidth: 560 }}
              >
                {[
                  { title: 'AI Syllabus', desc: 'A modular path shaped to your exact level and pace — reshuffled as you go.' },
                  { title: 'Quiz to Skip', desc: 'Already know it? Prove it in a short assessment and jump straight ahead.' },
                  { title: 'Grounded Tutor', desc: "Ask anything; every answer cites the exact moment in the lesson transcript." },
                ].map(f => (
                  <div key={f.title} style={{ background: '#0a0e11', border: '1px solid #1c2326', borderRadius: 12, padding: '16px 14px' }}>
                    <div style={{ fontFamily: 'Hanken Grotesk, sans-serif', fontWeight: 600, fontSize: 13, color: '#f2f3f9', marginBottom: 6 }}>{f.title}</div>
                    <div style={{ fontFamily: 'Hanken Grotesk, sans-serif', fontSize: 12, color: '#71768a', lineHeight: 1.5 }}>{f.desc}</div>
                  </div>
                ))}
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
          background: '#04050a',
          pointerEvents: 'none',
        }} />
      </div>

      {/* Divider line */}
      <div style={{ height: 1, background: '#1c2326', maxWidth: 1200, margin: '0 auto 0', marginLeft: 32, marginRight: 32 }} />

      {/* How It Works */}
      <HowItWorks />

      {/* Divider */}
      <div style={{ height: 1, background: '#1c2326', maxWidth: 1200, margin: '0 32px' }} />

      {/* Feature Grid */}
      <FeatureGrid />

      {/* Divider */}
      <div style={{ height: 1, background: '#1c2326', maxWidth: 1200, margin: '0 32px' }} />

      {/* Community */}
      <CommunitySection />

      {/* Footer CTA */}
      <FooterCTA onGetStarted={onGetStarted} />
    </div>
  )
}
