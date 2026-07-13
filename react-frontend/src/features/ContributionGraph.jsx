import React, { useState, useEffect, useMemo } from 'react';
import { CalendarDays, Loader2 } from 'lucide-react';

const API = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`;

const DAY_MS = 24 * 60 * 60 * 1000;

function levelForCount(count) {
  if (count <= 0) return 0;
  if (count === 1) return 1;
  if (count <= 3) return 2;
  if (count <= 6) return 3;
  return 4;
}

const LEVEL_CLASSES = [
  'bg-white/5',
  'bg-cyan-500/20',
  'bg-cyan-500/40',
  'bg-cyan-500/70',
  'bg-cyan-500',
];

const MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function buildWeeks(countsByDate) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const start = new Date(today.getTime() - 364 * DAY_MS);
  // Left-pad back to the most recent Sunday on/before `start` so columns align to calendar weeks.
  const paddedStart = new Date(start.getTime() - start.getDay() * DAY_MS);

  const days = [];
  for (let t = paddedStart.getTime(); t <= today.getTime(); t += DAY_MS) {
    const d = new Date(t);
    const iso = d.toISOString().slice(0, 10);
    days.push({ date: iso, day: d.getDate(), month: d.getMonth(), count: countsByDate[iso] || 0 });
  }

  const weeks = [];
  for (let i = 0; i < days.length; i += 7) {
    weeks.push(days.slice(i, i + 7));
  }
  return weeks;
}

export function ContributionGraph({ token }) {
  const [days, setDays] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/users/me/activity`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(d => {
        setDays(d.days || []);
        setLoading(false);
      })
      .catch(() => {
        setDays([]);
        setLoading(false);
      });
  }, [token]);

  const weeks = useMemo(() => {
    const countsByDate = {};
    (days || []).forEach(d => { countsByDate[d.date] = d.count; });
    return buildWeeks(countsByDate);
  }, [days]);

  const monthLabels = useMemo(() => {
    const labels = [];
    let lastMonth = null;
    weeks.forEach((week, i) => {
      const firstDay = week[0];
      if (firstDay.month !== lastMonth) {
        labels.push({ index: i, label: MONTH_LABELS[firstDay.month] });
        lastMonth = firstDay.month;
      }
    });
    return labels;
  }, [weeks]);

  const totalActivity = (days || []).reduce((sum, d) => sum + d.count, 0);

  return (
    <div className="glass-card p-6">
      <h3 className="text-xl font-bold mb-1 flex items-center gap-2">
        <CalendarDays className="w-5 h-5 text-cyan" /> Learning Activity
      </h3>
      <p className="text-xs text-slate-400 mb-6">
        {loading ? 'Loading...' : `${totalActivity} completions in the last year`}
      </p>

      {loading ? (
        <div className="h-32 flex items-center justify-center">
          <Loader2 className="w-6 h-6 animate-spin text-cyan" />
        </div>
      ) : (
        <div className="overflow-x-auto">
          <div className="inline-block min-w-full">
            <div
              className="grid mb-1 text-[10px] text-slate-500 font-mono"
              style={{ gridTemplateColumns: `repeat(${weeks.length}, minmax(0, 1fr))`, gap: '3px' }}
            >
              {weeks.map((_, i) => {
                const found = monthLabels.find(m => m.index === i);
                return <div key={i}>{found ? found.label : ''}</div>;
              })}
            </div>
            <div
              className="grid"
              style={{
                gridTemplateColumns: `repeat(${weeks.length}, minmax(0, 1fr))`,
                gridAutoFlow: 'column',
                gap: '3px',
              }}
            >
              {weeks.map((week, wi) => (
                <div key={wi} className="grid grid-rows-7 gap-[3px]">
                  {week.map(d => (
                    <div
                      key={d.date}
                      title={`${d.count} ${d.count === 1 ? 'activity' : 'activities'} on ${d.date}`}
                      className={`w-3 h-3 rounded-sm ${LEVEL_CLASSES[levelForCount(d.count)]}`}
                    />
                  ))}
                </div>
              ))}
            </div>
            <div className="flex items-center gap-1.5 mt-3 text-[10px] text-slate-500 font-mono">
              <span>Less</span>
              {LEVEL_CLASSES.map((cls, i) => (
                <div key={i} className={`w-3 h-3 rounded-sm ${cls}`} />
              ))}
              <span>More</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
