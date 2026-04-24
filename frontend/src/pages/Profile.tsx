import { useState, useEffect } from 'react';
import type { TelegramUser } from '../hooks/useTelegramUser';
import { getMe, getPayments } from '../services/api';

interface ProfileProps {
  user: TelegramUser | null;
}

interface UserProfile {
  wallet_balance: number;
  rank: string;
  total_earnings: number;
  tasks_completed: number;
  active_agents: number;
}

interface Payment {
  id: string;
  amount: number;
  currency: string;
  status: string;
  created_at: string;
}

const RANK_META: Record<string, { color: string; emoji: string }> = {
  bronze:   { color: '#CD7F32', emoji: '🥉' },
  silver:   { color: '#C0C0C0', emoji: '🥈' },
  gold:     { color: '#FFD700', emoji: '🥇' },
  platinum: { color: '#E5E4E2', emoji: '💎' },
  diamond:  { color: '#00E5FF', emoji: '💠' },
};

export function Profile({ user }: ProfileProps) {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [payments, setPayments] = useState<Payment[]>([]);
  const displayName = user
    ? `${user.first_name}${user.last_name ? ' ' + user.last_name : ''}`
    : 'Creator';

  useEffect(() => {
    getMe().then(setProfile).catch(() => {});
    getPayments().then(setPayments).catch(() => {});
  }, []);

  const rankKey = (profile?.rank || 'bronze').toLowerCase();
  const rankMeta = RANK_META[rankKey] || RANK_META.bronze;

  return (
    <div style={{ padding: '20px 16px 100px' }}>
      <div style={{ fontSize: '22px', fontWeight: '800', marginBottom: '20px' }}>👤 Profile</div>

      {/* Profile/Rank Card */}
      <div style={{
        padding: '24px', background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(255, 0, 110, 0.2))',
        border: '3px solid var(--war-purple)', textAlign: 'center', marginBottom: '24px'
      }}>
        <div className="label" style={{ marginBottom: '8px', color: 'var(--war-gray-700)' }}>YOUR COMBAT RANK</div>
        <div style={{
          fontFamily: 'var(--font-display)', fontSize: '64px', fontWeight: '900',
          color: 'white', lineHeight: '1', textShadow: `0 0 20px ${rankMeta.color}`, marginBottom: '16px',
        }}>{rankMeta.emoji} {rankKey.toUpperCase()}</div>
        
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: '8px',
          padding: '4px 12px', background: 'var(--war-cyan)', color: 'var(--war-black)',
          fontFamily: 'var(--font-mono)', fontSize: '14px', fontWeight: '700', marginBottom: '16px'
        }}>
          {displayName}
        </div>
        
        <div style={{ width: '100%', height: '8px', background: 'rgba(255,255,255,0.1)', border: '1px solid var(--war-gray-700)', marginBottom: '8px', overflow: 'hidden' }}>
          <div style={{ height: '100%', width: `${Math.min(100, (profile?.total_earnings || 0) / 100)}%`, background: 'linear-gradient(90deg, var(--war-cyan), var(--war-purple))', transition: 'width 0.5s ease' }}></div>
        </div>
        <div style={{ fontSize: '11px', color: 'rgba(255, 255, 255, 0.5)' }}>NEXT TIER AWAITING</div>
      </div>

      {/* Stats */}
      <div className="bento-grid" style={{ padding: 0, marginBottom: '24px', gridTemplateColumns: '1fr 1fr' }}>
        {[
          ['ACQUIRED FUNDS', profile ? `$${profile.total_earnings.toFixed(2)}` : '…'],
          ['MISSIONS WON', profile ? `${profile.tasks_completed}` : '…'],
          ['WAR CHEST', profile ? `$${profile.wallet_balance.toFixed(2)}` : '…'],
          ['MERCS HIRED', profile ? `${profile.active_agents}` : '…'],
        ].map(([label, value]) => (
          <div key={label} className="bento-item" style={{ padding: '16px', textAlign: 'center' }}>
            <div className="stat-number" style={{ fontSize: '24px', color: 'var(--war-cyan)' }}>{value}</div>
            <div className="label">{label}</div>
          </div>
        ))}
      </div>

      {/* Earnings History */}
      {payments.length > 0 && (
        <div style={{ marginBottom: '24px' }}>
          <div className="section-title" style={{ fontSize: '20px', marginBottom: '16px', color: 'var(--war-cyan)' }}>📜 PAYOUT LEDGER</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {payments.map((p) => (
              <div key={p.id} className="card-glass" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px' }}>
                <div>
                  <div style={{ fontFamily: 'var(--font-numbers)', fontSize: '16px', fontWeight: '700', color: 'white' }}>
                    {p.status === 'completed' ? '✅' : p.status === 'pending' ? '⏳' : '❌'} ${p.amount.toFixed(2)} {p.currency}
                  </div>
                  <div className="label" style={{ color: 'var(--war-gray-700)' }}>
                    {new Date(p.created_at).toLocaleDateString()}
                  </div>
                </div>
                <div style={{
                  fontSize: '11px', padding: '4px 10px', background: p.status === 'completed' ? 'var(--war-green)' : 'var(--war-gray-800)',
                  color: p.status === 'completed' ? 'var(--war-black)' : 'var(--war-muted)', fontFamily: 'var(--font-mono)', fontWeight: '800'
                }}>
                  {p.status.toUpperCase()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Invite */}
      <div style={{ background: 'linear-gradient(135deg, rgba(8, 14, 18, 0.9), rgba(18, 5, 12, 0.9))', border: '2px solid var(--war-pink)', padding: '24px', textAlign: 'center' }}>
        <div className="section-title" style={{ fontSize: '20px', marginBottom: '8px' }}>🚀 RECRUIT ALLIES</div>
        <div className="label" style={{ color: 'rgba(255, 255, 255, 0.6)', marginBottom: '20px' }}>Extract 10% of your ally's initial spoils</div>
        <button className="btn-primary" style={{ width: '100%' }}>
          <span className="btn-text">COPY INVITE LINK</span>
        </button>
      </div>
    </div>
  );
}
