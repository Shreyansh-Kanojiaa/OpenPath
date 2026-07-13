import React, { useState, useEffect } from 'react';
import { UserCog, Sparkles } from 'lucide-react';
import { ContributionGraph } from './ContributionGraph';

const API = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`;

export function AccountSettings({ token }) {
  const [settings, setSettings] = useState(null);
  const [usernameInput, setUsernameInput] = useState('');
  const [savingUsername, setSavingUsername] = useState(false);

  const [skills, setSkills] = useState([]);
  const [skillInput, setSkillInput] = useState('');
  const [savingSkills, setSavingSkills] = useState(false);

  const authHeaders = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  };

  const loadSettings = () => {
    fetch(`${API}/account/settings`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(d => {
        setSettings(d);
        setUsernameInput(d.username);
        setSkills(d.known_skills);
      });
  };

  useEffect(() => {
    loadSettings();
  }, [token]);

  const saveUsername = async (e) => {
    e.preventDefault();
    setSavingUsername(true);
    try {
      const res = await fetch(`${API}/account/username`, {
        method: 'PATCH',
        headers: authHeaders,
        body: JSON.stringify({ username: usernameInput }),
      });
      const body = await res.json();
      if (!res.ok) {
        const detail = body.detail;
        throw new Error(typeof detail === 'string' ? detail : detail?.message || 'Failed to update username');
      }
      loadSettings();
    } catch (err) {
      alert(err.message);
    } finally {
      setSavingUsername(false);
    }
  };

  const addSkill = () => {
    const value = skillInput.trim();
    if (!value) return;
    const exists = skills.some(s => s.toLowerCase() === value.toLowerCase());
    if (!exists) setSkills(prev => [...prev, value]);
    setSkillInput('');
  };

  const removeSkill = (skill) => {
    setSkills(prev => prev.filter(s => s !== skill));
  };

  const handleSkillKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addSkill();
    }
  };

  const saveSkills = async () => {
    setSavingSkills(true);
    try {
      const res = await fetch(`${API}/account/skills`, {
        method: 'PUT',
        headers: authHeaders,
        body: JSON.stringify({ skills }),
      });
      if (!res.ok) throw new Error('Failed to save skills');
      const body = await res.json();
      setSkills(body.known_skills);
    } catch (err) {
      alert(err.message);
    } finally {
      setSavingSkills(false);
    }
  };

  if (!settings) {
    return <div className="max-w-4xl mx-auto px-5 sm:px-8 py-28 md:py-32 w-full min-h-screen" />;
  }

  const nextChangeDate = settings.next_username_change_allowed_at
    ? new Date(settings.next_username_change_allowed_at).toLocaleDateString()
    : null;

  return (
    <div className="max-w-4xl mx-auto px-5 sm:px-8 py-28 md:py-32 w-full min-h-screen">
      <header className="mb-12 md:mb-16">
        <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold font-display tracking-tight mb-4">Account Settings</h2>
        <p className="text-base sm:text-xl text-slate-400 font-sans">Customize your profile and track your progress.</p>
      </header>

      <div className="space-y-8">
        <div className="glass-card p-6 sm:p-10">
          <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <UserCog className="w-6 h-6 text-blue" /> Profile
          </h3>
          <form onSubmit={saveUsername} className="max-w-md">
            <label className="text-[10px] uppercase tracking-widest text-slate-500 font-mono block mb-2">Username / Display Name</label>
            <div className="flex gap-2">
              <input
                value={usernameInput}
                onChange={e => setUsernameInput(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded px-4 py-3 text-sm focus:border-blue/50 focus:ring-1 focus:ring-blue/20 transition-all"
                disabled={!settings.can_change_username}
                required
              />
              <button
                type="submit"
                disabled={savingUsername || !settings.can_change_username}
                className="shrink-0 px-6 py-3 text-xs uppercase tracking-widest font-bold bg-blue text-charcoal-900 rounded hover:shadow-blue-glow transition-all disabled:opacity-50"
              >
                {savingUsername ? 'Saving...' : 'Save'}
              </button>
            </div>
            {!settings.can_change_username && nextChangeDate && (
              <p className="text-xs text-slate-500 mt-2">Next change available {nextChangeDate}.</p>
            )}
          </form>
        </div>

        <div className="glass-card p-6 sm:p-10">
          <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Sparkles className="w-6 h-6 text-blue" /> Skills You Already Know
          </h3>
          <p className="text-xs text-slate-400 mb-4 leading-relaxed">
            Saved here once — the Job Readiness Calculator will use this list automatically.
          </p>
          <div className="flex gap-2">
            <input
              value={skillInput}
              onChange={e => setSkillInput(e.target.value)}
              onKeyDown={handleSkillKeyDown}
              placeholder="e.g. Python, Docker — press Enter to add"
              className="w-full bg-white/5 border border-white/10 rounded px-4 py-3 text-sm focus:border-blue/50 focus:ring-1 focus:ring-blue/20 transition-all"
            />
            <button
              type="button"
              onClick={addSkill}
              className="shrink-0 px-4 py-3 text-xs uppercase tracking-widest font-bold bg-white/5 border border-white/10 rounded hover:bg-white/10 transition-all"
            >
              Add
            </button>
          </div>
          {skills.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {skills.map(skill => (
                <span
                  key={skill}
                  className="flex items-center gap-1.5 text-xs px-3 py-1 bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 rounded-full"
                >
                  {skill}
                  <button
                    type="button"
                    onClick={() => removeSkill(skill)}
                    className="hover:text-white transition-colors"
                    aria-label={`Remove ${skill}`}
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          )}
          <button
            type="button"
            onClick={saveSkills}
            disabled={savingSkills}
            className="mt-6 px-6 py-3 text-xs uppercase tracking-widest font-bold bg-blue text-charcoal-900 rounded hover:shadow-blue-glow transition-all disabled:opacity-50"
          >
            {savingSkills ? 'Saving...' : 'Save Skills'}
          </button>
        </div>

        <ContributionGraph token={token} />
      </div>
    </div>
  );
}
