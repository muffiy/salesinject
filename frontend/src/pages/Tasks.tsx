import { useState, useEffect } from 'react';
import { TaskCard } from '../components/UI';
import { getTasks, claimTask, getMySubmissions } from '../services/api';

interface Task {
  id: string;
  title: string;
  niche: string;
  reward_amount: number;
  status: string;
  description?: string;
}

interface Submission {
  id: string;
  task_id: string;
  task_title: string;
  task_niche: string;
  reward_amount: number;
  status: string;
}

const FILTERS = ['All', 'Open', 'My Tasks'];

const STATUS_COLOR: Record<string, string> = {
  pending: 'var(--si-muted)', approved: 'var(--si-green)', rejected: 'var(--si-accent-2)',
};

export function Tasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [filter, setFilter] = useState('All');
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [claiming, setClaiming] = useState(false);
  const [claimError, setClaimError] = useState('');

  useEffect(() => {
    Promise.all([getTasks(), getMySubmissions()])
      .then(([t, s]) => { setTasks(t); setSubmissions(s); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const myTaskIds = new Set(submissions.map((s) => s.task_id));

  const filtered = filter === 'My Tasks'
    ? tasks.filter((t) => myTaskIds.has(t.id))
    : filter === 'Open'
      ? tasks.filter((t) => t.status === 'open')
      : tasks;

  const handleClaim = async (taskId: string) => {
    setClaiming(true); setClaimError('');
    try {
      await claimTask(taskId);
      const [t, s] = await Promise.all([getTasks(), getMySubmissions()]);
      setTasks(t); setSubmissions(s);
      setSelectedTask(null);
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to claim task.';
      setClaimError(msg);
    } finally {
      setClaiming(false);
    }
  };

  // ── Task detail view ──────────────────────────────────────────────────────
  if (selectedTask) {
    const alreadyClaimed = myTaskIds.has(selectedTask.id);
    const mySub = submissions.find((s) => s.task_id === selectedTask.id);
    return (
      <div style={{ padding: '20px 16px 100px' }}>
        <button
          onClick={() => { setSelectedTask(null); setClaimError(''); }}
          className="label"
          style={{ background: 'none', border: 'none', color: 'var(--war-cyan)', fontSize: '14px', cursor: 'pointer', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '6px' }}
        >
          ← RETREAT
        </button>
        <div className="card-glass" style={{ padding: '24px' }}>
          <div className="label" style={{ marginBottom: '8px' }}>🎯 {selectedTask.niche}</div>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '24px', fontWeight: '900', textTransform: 'uppercase', marginBottom: '16px' }}>{selectedTask.title}</h2>
          {selectedTask.description && (
            <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6', marginBottom: '20px' }}>
              {selectedTask.description}
            </div>
          )}
          <div style={{ background: 'rgba(0, 245, 255, 0.1)', border: '2px solid var(--war-cyan)', padding: '16px', marginBottom: '20px' }}>
            <div className="label" style={{ color: 'var(--war-cyan)' }}>BOUNTY</div>
            <div className="stat-number">${selectedTask.reward_amount.toFixed(2)}</div>
          </div>
          {claimError && (
            <div style={{ color: 'var(--war-red)', fontSize: '13px', marginBottom: '12px', fontFamily: 'var(--font-mono)' }}>[ERROR] {claimError}</div>
          )}
          {mySub ? (
            <div style={{ textAlign: 'center', padding: '16px', background: 'rgba(26, 26, 26, 0.6)', border: '2px solid var(--war-gray-700)' }}>
              <div className="label" style={{ color: 'var(--war-gray-700)' }}>DEPLOYMENT STATUS</div>
              <div style={{ fontSize: '18px', fontWeight: '800', marginTop: '4px', color: STATUS_COLOR[mySub.status] || 'white', fontFamily: 'var(--font-mono)' }}>
                {mySub.status.toUpperCase()}
              </div>
            </div>
          ) : (
            <button
              onClick={() => handleClaim(selectedTask.id)}
              disabled={claiming || alreadyClaimed}
              className="btn-primary"
              style={{ width: '100%', opacity: claiming ? 0.7 : 1 }}
            >
              <span className="btn-glow"></span>
              <span className="btn-text">{claiming ? 'DEPLOYING...' : 'DEPLOY MERCENARY'}</span>
              {!claiming && <span className="btn-icon">⚔️</span>}
            </button>
          )}
        </div>
      </div>
    );
  }

  // ── Task list view ────────────────────────────────────────────────────────
  return (
    <div style={{ padding: '20px 16px 100px' }}>
      <div className="section-title" style={{ marginBottom: '20px', color: 'var(--war-cyan)' }}>⚔️ BATTLES</div>

      {/* Filter tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', overflowX: 'auto' }}>
        {FILTERS.map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{
              padding: '8px 16px',
              border: '2px solid ' + (filter === f ? 'var(--war-purple)' : 'var(--war-gray-700)'),
              background: filter === f ? 'var(--war-purple)' : 'transparent',
              color: filter === f ? 'white' : 'rgba(255, 255, 255, 0.6)',
              fontFamily: 'var(--font-mono)', fontSize: '11px', fontWeight: '600', textTransform: 'uppercase',
              cursor: 'pointer', whiteSpace: 'nowrap', transition: 'all 0.2s',
            }}
          >{f}</button>
        ))}
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--si-muted)' }}>Loading missions…</div>
      ) : filtered.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--si-muted)' }}>
          <div style={{ fontSize: '32px', marginBottom: '8px' }}>📭</div>
          <div>No missions found.</div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {filtered.map((task) => (
            <div key={task.id} style={{ position: 'relative' }}>
              <TaskCard
                title={task.title}
                niche={task.niche}
                reward={task.reward_amount}
                status={task.status}
                onClick={() => setSelectedTask(task)}
              />
              {myTaskIds.has(task.id) && (
                <div style={{
                  position: 'absolute', top: '12px', right: '12px',
                  background: 'rgba(0,229,160,0.15)', borderRadius: '8px',
                  padding: '2px 8px', fontSize: '10px', color: 'var(--si-green)', fontWeight: '600',
                }}>CLAIMED</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
