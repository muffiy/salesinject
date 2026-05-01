import { useState, useEffect, useCallback } from 'react';
import { getAgents, createAgent, deleteAgent, runAgentTask, pollUntilDone } from '../services/api';


interface Agent {
  id: string;
  name: string;
  niche: string;
  performance_score: number;
  tasks_completed: number;
  total_earnings: number;
}

interface AdResult {
  hook: string;
  format: string;
  angle: string;
  caption: string;
}

// ── Styles ─────────────────────────────────────────────────────────────────────

const overlayStyle: React.CSSProperties = {
  position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)',
  backdropFilter: 'blur(10px)', zIndex: 200,
  display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px'
};

const sheetStyle: React.CSSProperties = {
  background: 'rgba(26, 26, 26, 0.9)', border: '3px solid var(--war-purple)',
  padding: '28px 20px', width: '100%', maxWidth: '430px', boxShadow: '0 0 40px rgba(139, 92, 246, 0.3)',
};

// ── Sub-components ─────────────────────────────────────────────────────────────

function AgentCard({
  agent,
  onDelete,
  onTrain,
}: {
  agent: Agent;
  onDelete: (id: string) => void;
  onTrain: (agent: Agent) => void;
}) {
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    setDeleting(true);
    await onDelete(agent.id);
    setDeleting(false);
  };

  return (
    <div className="card-glass" style={{ marginBottom: '16px', padding: '20px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
        <div>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: '20px', fontWeight: '800', textTransform: 'uppercase', marginBottom: '4px' }}>
            ⚡ {agent.name}
          </div>
          <div className="label">
            🎯 {agent.niche}
          </div>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <div style={{
            padding: '4px 10px', background: 'var(--war-green)',
            fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'black', fontWeight: '800',
          }}>READY</div>
          <button
            onClick={handleDelete}
            disabled={deleting}
            style={{
              background: 'transparent', border: '2px solid var(--war-red)',
              color: 'var(--war-red)', cursor: 'pointer', padding: '4px 8px', fontSize: '12px',
            }}
          >
            {deleting ? '…' : '💀'}
          </button>
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', marginBottom: '16px', background: 'rgba(0,0,0,0.5)', padding: '12px', border: '1px solid var(--war-gray-700)' }}>
        {[
          ['MISSIONS', agent.tasks_completed.toString()],
          ['BOUNTY', `$${agent.total_earnings.toFixed(2)}`],
          ['SCORE', agent.performance_score.toFixed(1)],
        ].map(([l, v]) => (
          <div key={l} style={{ textAlign: 'center' }}>
            <div className="stat-number" style={{ fontSize: '18px' }}>{v}</div>
            <div className="label" style={{ fontSize: '9px' }}>{l}</div>
          </div>
        ))}
      </div>

      {/* Train button */}
      <button
        onClick={() => onTrain(agent)}
        className="btn-ghost"
        style={{ width: '100%' }}
      >
        🧠 UPGRADE MERC
      </button>
    </div>
  );
}


function CreateModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [name, setName] = useState('');
  const [niche, setNiche] = useState('');
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState('');

  const handleSubmit = async () => {
    if (!name.trim() || !niche.trim()) { setErr('Both fields are required.'); return; }
    setLoading(true); setErr('');
    try {
      await createAgent({ name: name.trim(), niche: niche.trim() });
      onCreated();
      onClose();
    } catch {
      setErr('Failed to create agent. Try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={overlayStyle} onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div style={sheetStyle}>
        <div className="section-title" style={{ fontSize: '24px', marginBottom: '20px', color: 'var(--war-cyan)' }}>🤖 HIRE MERC</div>
        <div className="input-wrapper">
          <label className="input-label">CODENAME</label>
          <input className="input-terminal" placeholder="e.g. AdBot Alpha" value={name} onChange={(e) => setName(e.target.value)} />
          <span className="input-cursor">_</span>
        </div>
        <div className="input-wrapper">
          <label className="input-label">SPECIALTY</label>
          <input className="input-terminal" placeholder="e.g. Fitness, Beauty" value={niche} onChange={(e) => setNiche(e.target.value)} />
          <span className="input-cursor">_</span>
        </div>
        {err && <div style={{ color: 'var(--war-red)', fontSize: '13px', marginBottom: '12px', fontFamily: 'var(--font-mono)' }}>[ERROR] {err}</div>}
        <button className="btn-primary" style={{ width: '100%' }} onClick={handleSubmit} disabled={loading}>
          <span className="btn-text">{loading ? 'INITIALIZING…' : 'DEPLOY NOW'}</span>
        </button>
        <button
          onClick={onClose}
          style={{ width: '100%', marginTop: '10px', padding: '12px', background: 'none', border: '1px solid var(--war-gray-700)', color: 'rgba(255, 255, 255, 0.6)', cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: '12px' }}
        >ABORT</button>
      </div>
    </div>
  );
}


function TrainModal({ agent, onClose }: { agent: Agent; onClose: () => void }) {
  const [productName, setProductName] = useState('');
  const [loading, setLoading] = useState(false);
  const [statusText, setStatusText] = useState('');
  const [result, setResult] = useState<AdResult | null>(null);
  const [err, setErr] = useState('');

  const handleTrain = async () => {
    if (!productName.trim()) { setErr('Enter a product name.'); return; }
    setLoading(true); setErr(''); setStatusText('Queuing task…');
    try {
      // Step 1: Dispatch to Celery — get task_id (202 Accepted)
      const { task_id } = await runAgentTask({ agent_id: agent.id, niche: agent.niche, directive: productName.trim() });
      setStatusText('Agent is working… ⏳');
      // Step 2: Poll until done (2s interval, 2 min timeout)
      const data = await pollUntilDone(task_id);
      setResult(data.ad_idea as unknown as AdResult ?? data as unknown as AdResult);
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : 'Agent task failed. Try again.');
    } finally {
      setLoading(false);
      setStatusText('');
    }
  };

  return (
    <div style={overlayStyle} onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div style={sheetStyle}>
        <div className="section-title" style={{ fontSize: '24px', marginBottom: '6px', color: 'var(--war-cyan)' }}>🧠 UPGRADE</div>
        <div className="label" style={{ marginBottom: '20px' }}>
          {agent.name} · {agent.niche}
        </div>

        {!result ? (
          <>
            <div className="input-wrapper">
              <label className="input-label">TARGET DIRECTIVE</label>
              <input className="input-terminal" placeholder="Product / service name" value={productName} onChange={(e) => setProductName(e.target.value)} disabled={loading} />
              <span className="input-cursor">_</span>
            </div>
            {err && <div style={{ color: 'var(--war-red)', fontSize: '13px', marginBottom: '12px', fontFamily: 'var(--font-mono)' }}>[ERROR] {err}</div>}
            {statusText && (
              <div style={{ color: 'var(--war-cyan)', fontSize: '13px', marginBottom: '12px', textAlign: 'center', fontFamily: 'var(--font-mono)' }}>
                {statusText}
              </div>
            )}
            <button className="btn-primary" style={{ width: '100%' }} onClick={handleTrain} disabled={loading}>
              <span className="btn-text">{loading ? 'WORKING…' : 'GENERATE AMMO'}</span>
            </button>
          </>
        ) : (
          <div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {([
                ['HOOK', result.hook],
                ['FORMAT', result.format],
                ['ANGLE', result.angle],
                ['CAPTION', result.caption],
              ] as [string, string][]).map(([label, value]) => (
                <div key={label} style={{ background: 'rgba(0,0,0,0.5)', border: '1px solid var(--war-gray-700)', padding: '14px' }}>
                  <div className="label" style={{ marginBottom: '4px' }}>{label}</div>
                  <div style={{ fontSize: '14px', fontWeight: '500', color: 'white' }}>{value}</div>
                </div>
              ))}
            </div>
            <button className="btn-primary" onClick={onClose} style={{ width: '100%', marginTop: '16px' }}>DONE</button>
          </div>
        )}

        {!result && !loading && (
          <button
            onClick={onClose}
            style={{ width: '100%', marginTop: '10px', padding: '12px', background: 'none', border: '1px solid var(--war-gray-700)', color: 'rgba(255, 255, 255, 0.6)', cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: '12px' }}
          >ABORT</button>
        )}
      </div>
    </div>
  );
}



// ── Main Page ──────────────────────────────────────────────────────────────────

export function Agents() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [trainingAgent, setTrainingAgent] = useState<Agent | null>(null);
  const [err, setErr] = useState('');

  const fetchAgents = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getAgents();
      setAgents(data);
    } catch {
      setErr('Could not load agents.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAgents(); }, [fetchAgents]);

  const handleDelete = async (id: string) => {
    try {
      await deleteAgent(id);
      setAgents((prev) => prev.filter((a) => a.id !== id));
    } catch {
      setErr('Delete failed.');
    }
  };

  return (
    <div style={{ padding: '20px 16px 100px', flex: 1 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div className="section-title" style={{ color: 'var(--war-cyan)' }}>🤖 MERCENARIES</div>
        <div className="label">{agents.length} ACTIVE</div>
      </div>

      {err && (
        <div style={{ background: 'rgba(255,101,132,0.1)', border: '1px solid var(--si-accent-2)', borderRadius: '12px', padding: '12px', marginBottom: '16px', fontSize: '13px', color: 'var(--si-accent-2)' }}>
          {err}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--si-muted)' }}>Loading agents…</div>
      ) : agents.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--si-muted)' }}>
          <div style={{ fontSize: '40px', marginBottom: '12px' }}>🤖</div>
          <div style={{ fontWeight: '600', marginBottom: '6px' }}>No agents yet</div>
          <div style={{ fontSize: '13px' }}>Create your first AI agent to start earning.</div>
        </div>
      ) : (
        agents.map((agent) => (
          <AgentCard
            key={agent.id}
            agent={agent}
            onDelete={handleDelete}
            onTrain={(a) => setTrainingAgent(a)}
          />
        ))
      )}

      {/* Create new agent button */}
      <button
        onClick={() => setShowCreate(true)}
        style={{
          width: '100%', padding: '16px',
          background: 'rgba(0, 245, 255, 0.05)', border: '2px dashed var(--war-cyan)',
          color: 'var(--war-cyan)', fontFamily: 'var(--font-mono)', fontSize: '14px', fontWeight: '700',
          cursor: 'pointer', textTransform: 'uppercase', transition: 'all 0.2s',
        }}
        onMouseEnter={e => { e.currentTarget.style.background = 'rgba(0, 245, 255, 0.1)'; e.currentTarget.style.boxShadow = '0 0 20px rgba(0, 245, 255, 0.2)'; }}
        onMouseLeave={e => { e.currentTarget.style.background = 'rgba(0, 245, 255, 0.05)'; e.currentTarget.style.boxShadow = 'none'; }}
      >
        + RECRUIT MERCENARY
      </button>

      {showCreate && (
        <CreateModal
          onClose={() => setShowCreate(false)}
          onCreated={fetchAgents}
        />
      )}
      {trainingAgent && (
        <TrainModal
          agent={trainingAgent}
          onClose={() => setTrainingAgent(null)}
        />
      )}
    </div>
  );
}
