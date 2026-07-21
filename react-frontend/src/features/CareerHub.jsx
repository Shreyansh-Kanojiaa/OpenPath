import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import ForceGraph2D from 'react-force-graph-2d';
import { Briefcase, Target, Map, Clock, CheckCircle2, ChevronRight, Loader2 } from 'lucide-react';
import { BadgeGrid } from './Badges';

const API = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`;

function SkillGraph({ token }) {
  const [data, setData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const graphRef = useRef();
  const containerRef = useRef();

  const [pulse, setPulse] = useState(1);
  const [dims, setDims] = useState({ width: 0, height: 0 });

  useEffect(() => {
    fetch(`${API}/career/skill-graph`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch(e => {
        console.error(e);
        setLoading(false);
      });
  }, [token]);

  useEffect(() => {
    if (loading) return;
    let t = 0;
    const interval = setInterval(() => {
      t += 0.1;
      setPulse(1 + Math.sin(t) * 0.3);
    }, 50);
    return () => clearInterval(interval);
  }, [loading]);

  // ForceGraph2D falls back to the window size unless explicitly told the
  // container's dimensions, which overflows this card's clipped bounds.
  useEffect(() => {
    if (loading || !containerRef.current) return;
    const el = containerRef.current;
    const update = () => setDims({ width: el.clientWidth, height: el.clientHeight });
    update();
    const ro = new ResizeObserver(update);
    ro.observe(el);
    return () => ro.disconnect();
  }, [loading]);

  if (loading) {
    return <div className="h-[400px] flex items-center justify-center text-slate-500"><Loader2 className="w-8 h-8 animate-spin text-cyan" /></div>;
  }

  return (
    <div ref={containerRef} className="h-[500px] w-full rounded-2xl overflow-hidden border border-white/5 bg-black/30 relative">
      <div className="absolute top-4 left-4 z-10 bg-black/50 p-3 rounded-2xl backdrop-blur border border-white/5 text-xs text-slate-300">
        <h4 className="font-bold text-white mb-2 uppercase tracking-wider text-xs">Skill Graph</h4>
        <div className="flex items-center gap-2 mb-1"><div className="w-3 h-3 rounded-2xl bg-mastered shadow-[0_0_8px_rgba(134,196,187,0.4)]" /> Mastered</div>
        <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-2xl bg-slate-600" /> Pending</div>
      </div>
      <ForceGraph2D
        ref={graphRef}
        width={dims.width}
        height={dims.height}
        graphData={data}
        nodeLabel="name"
        nodeColor={node => node.completed ? '#86c4bb' : '#475569'}
        nodeVal={node => node.completed ? 6 * pulse : 6}
        nodeRelSize={1}
        linkColor={() => 'rgba(255,255,255,0.1)'}
        linkWidth={1.5}
        backgroundColor="#00000000"
        onEngineStop={() => graphRef.current?.zoomToFit(400, 50)}
      />
    </div>
  );
}

export function CareerHub({ token, onGenerateClick, onManageSkillsClick }) {
  const [jobTitle, setJobTitle] = useState('');
  const [company, setCompany] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const calculateReadiness = async (e) => {
    e.preventDefault();
    if (!jobTitle) return;

    setLoading(true);
    try {
      const res = await fetch(`${API}/career/job-ready`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ job_title: jobTitle, company: company })
      });
      if (!res.ok) throw new Error('Failed');
      setResult(await res.json());
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-5 sm:px-8 py-28 md:py-32 w-full min-h-screen">
      <header className="mb-12 md:mb-16">
        <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold font-display tracking-tight mb-4">Career Hub</h2>
        <p className="text-base sm:text-xl text-slate-400 font-sans">Map your skills, calculate job readiness, and bridge the gap.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8">
        <div className="lg:col-span-2 space-y-8">
          <div className="glass-card p-6 sm:p-10 relative overflow-hidden">
            <div className="absolute top-[-20%] right-[-10%] w-[400px] h-[400px] bg-blue/5 blur-[100px] rounded-full pointer-events-none" />
            
            <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
              <Target className="w-6 h-6 text-blue" /> Job Ready Calculator
            </h3>
            
            <form onSubmit={calculateReadiness} className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
              <div>
                <label className="text-[10px] uppercase tracking-widest text-slate-500 font-mono block mb-2">Job Title / Role</label>
                <input 
                  value={jobTitle} onChange={e => setJobTitle(e.target.value)}
                  placeholder="e.g. DevOps Engineer"
                  className="w-full bg-white/5 border border-white/10 rounded px-4 py-3 text-sm focus:border-blue/50 focus:ring-1 focus:ring-blue/20 transition-all"
                  required
                />
              </div>
              <div>
                <label className="text-[10px] uppercase tracking-widest text-slate-500 font-mono block mb-2">Company (Optional)</label>
                <input 
                  value={company} onChange={e => setCompany(e.target.value)}
                  placeholder="e.g. CRED, Google"
                  className="w-full bg-white/5 border border-white/10 rounded px-4 py-3 text-sm focus:border-blue/50 focus:ring-1 focus:ring-blue/20 transition-all"
                />
              </div>
              {onManageSkillsClick && (
                <div className="md:col-span-2">
                  <button
                    type="button"
                    onClick={onManageSkillsClick}
                    className="text-xs text-slate-400 hover:text-cyan transition-colors underline underline-offset-2"
                  >
                    Manage skills you already know in Account Settings →
                  </button>
                </div>
              )}
              <div className="md:col-span-2">
                <button
                  type="submit" disabled={loading}
                  className="w-full py-4 bg-blue text-charcoal-900 font-bold uppercase tracking-widest text-sm rounded hover:shadow-blue-glow transition-all disabled:opacity-50"
                >
                  {loading ? 'Analyzing Profile...' : 'Calculate Readiness'}
                </button>
              </div>
            </form>

            {result && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="pt-8 border-t border-white/5">
                <div className="flex flex-col md:flex-row gap-8 md:gap-12 items-center mb-10">
                  <div className="relative w-48 h-48 flex-shrink-0">
                    <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                      <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
                      <motion.circle
                        cx="50" cy="50" r="45" fill="none"
                        stroke={result.readiness_percentage >= 80 ? '#86c4bb' : result.readiness_percentage >= 50 ? '#e0af68' : '#f7768e'}
                        strokeWidth="8" strokeLinecap="square" strokeDasharray={2 * Math.PI * 45}
                        strokeDashoffset={2 * Math.PI * 45 * (1 - (result.readiness_percentage / 100))}
                        initial={{ strokeDashoffset: 2 * Math.PI * 45 }}
                        animate={{ strokeDashoffset: 2 * Math.PI * 45 * (1 - (result.readiness_percentage / 100)) }}
                        transition={{ duration: 1.5, ease: [0.16, 1, 0.3, 1] }}
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-5xl font-display font-black">{result.readiness_percentage}%</span>
                      <span className="text-[10px] uppercase tracking-widest text-slate-500 font-mono mt-1">Ready</span>
                    </div>
                  </div>
                  
                  <div className="flex-1 space-y-6">
                    <div>
                      <h4 className="text-lg font-bold text-white mb-3">Estimated Time to Ready</h4>
                      <div className="flex items-center gap-2 text-blue font-mono bg-blue/10 px-4 py-2 rounded inline-flex">
                        <Clock className="w-4 h-4" /> {result.estimated_time}
                      </div>
                    </div>
                    <div>
                      <h4 className="text-lg font-bold text-white mb-3 text-rose-400">Missing Skills</h4>
                      <div className="flex flex-wrap gap-2">
                        {result.missing_skills.map((s, i) => (
                          <span key={i} className="text-xs px-3 py-1 bg-rose-500/10 border border-rose-500/20 text-rose-300 rounded-full">{s}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-black/30 rounded-2xl p-6 border border-white/5">
                  <h4 className="text-lg font-bold mb-4 flex items-center gap-2"><Map className="w-5 h-5 text-cyan" /> Recommended Roadmap</h4>
                  <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-[1px] before:bg-white/10">
                    {result.roadmap.map((step, i) => (
                      <div key={i} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                        <div className="flex items-center justify-center w-10 h-10 rounded-2xl border border-black bg-slate-800 text-slate-500 group-hover:bg-cyan group-hover:text-black group-hover:border-cyan shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 transition-colors z-10">
                          <span className="text-sm font-bold font-mono">{i + 1}</span>
                        </div>
                        <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] glass-card p-4 rounded-2xl shadow flex justify-between items-center gap-4 group-hover:border-cyan/30 transition-colors">
                          <p className="text-sm text-slate-300 leading-relaxed flex-1">{step}</p>
                          {onGenerateClick && (
                            <button
                              onClick={() => onGenerateClick(step)}
                              className="shrink-0 px-4 py-2 text-[10px] uppercase tracking-widest font-bold text-black bg-cyan rounded-2xl hover:scale-105 active:scale-95 transition-all shadow-blue-glow-sm opacity-0 group-hover:opacity-100"
                              title="Generate a course for this skill"
                            >
                              Build
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>

        <div className="lg:col-span-1 space-y-8">
          <div className="glass-card p-6">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Briefcase className="w-5 h-5 text-cyan" /> Your Ecosystem
            </h3>
            <p className="text-xs text-slate-400 mb-6 leading-relaxed">
              Visualize your skills as a network. Glowing nodes represent skills you've mastered. Discover paths to new competencies.
            </p>
            <SkillGraph token={token} />
          </div>
          
          <div className="glass-card p-6 bg-blue/5 border-blue/20 rounded-2xl">
            <h3 className="text-lg font-bold mb-2 text-white">Verified Badges</h3>
            <p className="text-xs text-slate-400 mb-6">Complete paths to unlock verifiable micro-credentials.</p>
            <BadgeGrid token={token} />
          </div>
        </div>
      </div>
    </div>
  );
}
