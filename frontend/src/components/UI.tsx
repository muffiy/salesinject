import React from 'react';

interface StatCardProps {
  label: string;
  value: string;
  icon: string;
  accent: string;
  sub?: string;
}

export function StatCard({ label, value, icon, accent, sub }: StatCardProps) {
  return (
    <div className="bento-item" style={{ borderColor: accent, display: 'flex', flexDirection: 'column', gap: '8px' }}>
      <div style={{ fontSize: '24px' }}>{icon}</div>
      <div className="stat-number" style={{ color: accent }}>{value}</div>
      <div className="label" style={{ color: 'var(--si-muted)' }}>{label}</div>
      {sub && <div style={{ fontSize: '11px', color: 'var(--war-green)', fontFamily: 'var(--font-mono)' }}>{sub}</div>}
    </div>
  );
}

interface TaskCardProps {
  title: string;
  niche: string;
  reward: number;
  status: string;
  onClick?: () => void;
}

export function TaskCard({ title, niche, reward, status, onClick }: TaskCardProps) {
  const statusColor = status === 'open' ? 'var(--war-green)' : 'var(--war-gray-700)';
  return (
    <div
      onClick={onClick}
      className="card-glass"
      style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', padding: '16px' }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <div style={{ fontFamily: 'var(--font-display)', fontSize: '16px', fontWeight: '800', textTransform: 'uppercase' }}>{title}</div>
        <div className="label">🎯 {niche}</div>
        <div style={{ fontSize: '11px', color: statusColor, marginTop: '2px', fontFamily: 'var(--font-mono)' }}>
          ● {status.toUpperCase()}
        </div>
      </div>
      <div style={{
        background: 'rgba(0, 245, 255, 0.1)',
        border: '2px solid var(--war-cyan)',
        padding: '8px 14px',
        fontFamily: 'var(--font-numbers)',
        fontSize: '16px',
        fontWeight: '700',
        color: 'var(--war-cyan)',
        whiteSpace: 'nowrap',
      }}>
        +${reward}
      </div>
    </div>
  );
}

interface NavBarProps {
  active: string;
  onChange: (tab: string) => void;
}

export function NavBar({ active, onChange }: NavBarProps) {
  const tabs = [
    { id: 'dashboard', icon: '⚡', label: 'HOME' },
    { id: 'tasks', icon: '⚔️', label: 'BATTLES' },
    { id: 'agents', icon: '🤖', label: 'MERCS' },
    { id: 'profile', icon: '📊', label: 'STATS' },
  ];

  return (
    <nav className="mobile-nav" style={{
      position: 'fixed', bottom: 0, left: 0, right: 0,
      display: 'flex', background: 'rgba(10, 10, 10, 0.95)',
      backdropFilter: 'blur(20px)', borderTop: '2px solid var(--war-purple)',
      padding: '8px env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left)',
      zIndex: 1000
    }}>
      {tabs.map((tab, idx) => {
        // Insert a FAB in the middle for 'Map' or 'New Action'
        const isMiddle = idx === 2;
        return (
          <React.Fragment key={tab.id}>
            {isMiddle && (
              <button className="nav-item nav-fab" onClick={() => onChange('map')} style={{
                width: '56px', height: '56px', marginTop: '-28px',
                background: 'var(--gradient-rage)', border: '4px solid var(--war-black)',
                borderRadius: '50%', boxShadow: '0 8px 24px rgba(255, 0, 110, 0.5)',
                display: 'flex', alignItems: 'center', justifyContent: 'center'
              }}>
                <span className="nav-icon" style={{ fontSize: '32px', color: 'white' }}>🗺️</span>
              </button>
            )}
            <button
              className={`nav-item ${active === tab.id ? 'active' : ''}`}
              onClick={() => onChange(tab.id)}
              style={{
                flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px',
                padding: '8px', background: 'transparent', border: 'none',
                color: active === tab.id ? 'var(--war-cyan)' : 'rgba(255, 255, 255, 0.6)',
                transition: 'all 0.2s', position: 'relative'
              }}
            >
              <span className="nav-icon" style={{ fontSize: '24px', transition: 'transform 0.2s', transform: active === tab.id ? 'scale(1.2)' : 'none' }}>
                {tab.icon}
              </span>
              <span className="nav-label" style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', fontWeight: '600', textTransform: 'uppercase' }}>
                {tab.label}
              </span>
              {/* Optional notification badge for battles */}
              {tab.id === 'tasks' && (
                <span className="nav-badge" style={{
                  position: 'absolute', top: '4px', right: '20%', width: '18px', height: '18px',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: 'var(--war-red)', border: '2px solid var(--war-black)', borderRadius: '50%',
                  fontFamily: 'var(--font-mono)', fontSize: '10px', fontWeight: '700', color: 'white'
                }}>3</span>
              )}
            </button>
          </React.Fragment>
        );
      })}
    </nav>
  );
}

export interface MapProfileCardProps {
  data: any;
  onClose: () => void;
}

export function MapProfileCard({ data, onClose }: MapProfileCardProps) {
  if (!data) return null;

  return (
    <div className="card-glass" style={{
      position: 'absolute', top: '24px', right: '24px', width: '280px', padding: '20px', zIndex: 50, display: 'flex', flexDirection: 'column', gap: '12px',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ fontFamily: 'var(--font-display)', fontSize: '20px', fontWeight: '900', color: 'white', textTransform: 'uppercase' }}>{data.name}</div>
        <button onClick={onClose} style={{ background: 'transparent', border: '2px solid var(--war-red)', color: 'var(--war-red)', cursor: 'pointer', fontFamily: 'var(--font-mono)', fontWeight: 'bold' }}>X</button>
      </div>
      
      <div style={{ display: 'inline-block', padding: '4px 8px', background: 'var(--war-purple)', color: 'white', fontFamily: 'var(--font-mono)', fontSize: '11px', fontWeight: '800', textTransform: 'uppercase', width: 'fit-content' }}>
        {data.type}
      </div>

      {data.extraData && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '8px', borderTop: '1px solid var(--war-gray-700)', paddingTop: '12px' }}>
          {Object.entries(data.extraData).map(([key, value]) => (
             <div key={key} style={{ display: 'flex', justifyContent: 'space-between', background: 'rgba(0,0,0,0.5)', border: '1px solid var(--war-gray-800)', padding: '8px' }}>
               <span className="label" style={{ color: 'var(--war-cyan)' }}>{key}: </span>
               <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', fontWeight: '700', color: 'white' }}>{String(value)}</span>
             </div>
          ))}
        </div>
      )}
      
      <button className="btn-primary" style={{ marginTop: '12px', padding: '12px' }}>
        <span className="btn-text" style={{ fontSize: '12px' }}>INITIATE STRIKE</span>
      </button>
    </div>
  );
}
