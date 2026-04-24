import { useEffect, useState } from 'react';
import type { TelegramUser } from '../hooks/useTelegramUser';
import { StatCard, TaskCard } from '../components/UI';
import { getMe, getTasks, runAgentTask, pollUntilDone, getLatestScout } from '../services/api';
import { GlobalMap } from '../components/Map';
import type { MapDataPoint } from '../components/DeckGLMap';

interface DashboardProps {
  user: TelegramUser | null;
  onNavigate: (tab: string) => void;
}

interface UserProfile {
  wallet_balance: number;
  rank: string;
  total_earnings: number;
  tasks_completed: number;
  active_agents: number;
}

interface Task {
  id: string;
  title: string;
  niche: string;
  reward_amount: number;
  status: string;
}

const RANK_COLORS: Record<string, string> = {
  bronze: '#CD7F32', silver: '#C0C0C0', gold: '#FFD700', platinum: '#E5E4E2', diamond: '#00E5FF',
};

const MOCK_MAP_DATA: MapDataPoint[] = [
  { id: '1', name: 'OpenAI Marketing Bot', lat: 37.7749, lon: -122.4194, type: 'agent', extraData: { niche: 'SaaS', tasks: 120 } },
  { id: '2', name: 'Nike Paris Ad Campaign', lat: 48.8566, lon: 2.3522, type: 'business', extraData: { reach: '1.2M', CPC: '$0.40' } },
  { id: '3', name: 'Tokyo Fitness Agent', lat: 35.6762, lon: 139.6503, type: 'agent', extraData: { niche: 'Fitness', earnings: '$450.00' } },
  { id: '4', name: 'Dubai Real Estate Ad', lat: 25.2048, lon: 55.2708, type: 'business', extraData: { impressions: '340k', CPL: '$12.00' } },
  { id: '5', name: 'London Finance Agent', lat: 51.5074, lon: -0.1278, type: 'agent', extraData: { niche: 'Crypto', active: true } },
];

export function Dashboard({ user, onNavigate }: DashboardProps) {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [hotTasks, setHotTasks] = useState<Task[]>([]);
  const [scouting, setScouting] = useState(false);
  const [scoutError, setScoutError] = useState('');
  const [mapData, setMapData] = useState<MapDataPoint[]>(MOCK_MAP_DATA);
  
  const displayName = user?.first_name || 'Creator';

  const refreshScoutResults = async () => {
    try {
      const data = await getLatestScout();
      if (data && data.map_data && data.map_data.length > 0) {
        setMapData(data.map_data);
      }
    } catch (e) {
      console.warn('No scout data found or error fetching scout data.');
    }
  };

  const pollTaskStatus = async (taskId: string) => {
    await pollUntilDone(taskId);
  };

  const handleScout = async () => {
    setScouting(true);
    setScoutError('');
    try {
      const { task_id } = await runAgentTask('', 'General', 'Scout Mission', 'scout');
      await pollTaskStatus(task_id);
      await refreshScoutResults();
    } catch (e: any) {
      setScoutError(e.message || 'Scout failed.');
    } finally {
      setScouting(false);
    }
  };
  
  useEffect(() => {
    getMe().then(setProfile).catch(() => {});
    getTasks().then((tasks: Task[]) => setHotTasks(tasks.slice(0, 2))).catch(() => {});
    refreshScoutResults();
  }, []);

  return (
    <div style={{ paddingBottom: '100px', flex: 1, backgroundColor: 'var(--war-black)' }}>
      {/* SHOCK & AWE HERO SECTION (Mobile Adjusted) */}
      <section className="hero-section" style={{ position: 'relative', minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
        <div className="hero-bg" style={{ position: 'absolute', inset: 0, zIndex: 0 }}>
          <div className="grid-overlay" style={{
            position: 'absolute', inset: 0,
            backgroundImage: 'linear-gradient(rgba(139, 92, 246, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(139, 92, 246, 0.1) 1px, transparent 1px)',
            backgroundSize: '50px 50px', animation: 'grid-move 20s linear infinite'
          }}></div>
          <div className="gradient-orbs" style={{ position: 'absolute', inset: 0 }}></div>
          <div className="scan-line-container" style={{ position: 'absolute', inset: 0 }}></div>
        </div>
        
        <div className="hero-content" style={{ position: 'relative', zIndex: 10, maxWidth: '1200px', padding: '0 20px', textAlign: 'center', marginTop: '40px' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '8px 20px', background: 'rgba(139, 92, 246, 0.2)', border: '2px solid var(--war-purple)', marginBottom: '32px', position: 'relative', overflow: 'hidden' }}>
            <span className="badge-icon">⚔️</span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', fontWeight: '700', color: 'white' }}>VISIBILITY WAR GAME</span>
          </div>
          
          <h1 className="hero-title glitch" data-text="GENESIS MARKET" style={{ fontSize: 'clamp(40px, 12vw, 80px)' }}>
            GENESIS MARKET
          </h1>
          
          <p style={{ fontSize: 'clamp(14px, 4vw, 18px)', color: 'rgba(255, 255, 255, 0.7)', margin: '24px 0 40px', lineHeight: 1.6 }}>
            Turn marketing into a <span style={{ color: 'var(--war-cyan)', fontWeight: '700', textDecoration: 'underline', textDecorationColor: 'var(--war-pink)', textDecorationThickness: '3px', textUnderlineOffset: '4px' }}>real-time battle</span><br/>
            Deploy capital as ammunition. Hire influencers as mercenaries.
          </p>
          
          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', marginBottom: '40px', flexWrap: 'wrap' }}>
            <button className="btn-primary" onClick={() => onNavigate('tasks')}>
              <span className="btn-glow"></span>
              <span className="btn-text">ENTER BATTLEFIELD</span>
              <span className="btn-icon">→</span>
            </button>
            <button className="btn-ghost" onClick={() => onNavigate('agents')}>
              <span>VIEW MERCS</span>
              <span>▶</span>
            </button>
          </div>
          
          {/* Live Stats Ticker */}
          <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', padding: '16px', background: 'rgba(26, 26, 26, 0.6)', backdropFilter: 'blur(20px)', border: '2px solid var(--war-gray-700)', borderLeft: '4px solid var(--war-cyan)', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <span className="stat-number" style={{ fontSize: '24px' }}>$2.4M</span>
              <span className="label">DEPLOYED TODAY</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <span className="stat-number" style={{ fontSize: '24px', color: 'var(--war-purple)' }}>{profile ? profile.active_agents * 5 : '1,284'}</span>
              <span className="label">ACTIVE BATTLES</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <span className="stat-number" style={{ fontSize: '24px', color: 'var(--war-pink)' }}>847</span>
              <span className="label">BRANDS FIGHTING</span>
            </div>
          </div>
        </div>
      </section>

      {/* Actual user data section */}
      <div style={{ padding: '20px' }}>
        <div className="section-title" style={{ fontSize: '24px', marginBottom: '16px', color: 'var(--war-cyan)' }}>
          YOUR WAR ROOM
        </div>
        
        {/* Stats Grid */}
        <div className="bento-grid" style={{ padding: 0, marginBottom: '24px' }}>
          <StatCard icon="📋" label="Active Missions" value={profile ? hotTasks.length.toString() : '0'} accent="var(--war-cyan)" />
          <StatCard icon="🤖" label="My Mercs" value={profile ? profile.active_agents.toString() : '0'} accent="var(--war-purple)" />
          <StatCard icon="💰" label="War Chest" value={profile ? `$${profile.wallet_balance.toFixed(2)}` : '$0.00'} accent="var(--war-yellow)" />
        </div>

        {/* Global Map Preview */}
        <div className="card-glass" style={{ marginBottom: '24px', padding: '0', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', background: 'linear-gradient(90deg, var(--war-purple), transparent)', borderBottom: '2px solid var(--war-purple)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontFamily: 'var(--font-display)', fontSize: '18px', fontWeight: '800', color: 'white' }}>DOWNTOWN SECTOR</span>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              {scoutError && <span style={{ color: 'var(--war-red)', fontSize: '12px', fontFamily: 'var(--font-mono)' }}>[!] {scoutError}</span>}
              <button 
                className={scouting ? "btn-ghost" : "btn-primary"} 
                onClick={handleScout} 
                disabled={scouting}
                style={{ padding: '4px 12px', fontSize: '12px', letterSpacing: '1px' }}
              >
                {scouting ? "📡 SCANNING..." : "📡 SCOUT AREA (100 C)"}
              </button>
              <span className="label animate-glow">LIVE</span>
            </div>
          </div>
          <div style={{ height: '300px', flex: 1 }}>
            <GlobalMap data={mapData} />
          </div>
        </div>

        {/* Hot Missions */}
        <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: '20px', fontWeight: '800' }}>🔥 HOT TARGETS</div>
          <button onClick={() => onNavigate('tasks')} className="label" style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
            SEE ALL →
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {hotTasks.map((task) => (
            <TaskCard key={task.id} title={task.title} niche={task.niche} reward={task.reward_amount} status={task.status} onClick={() => onNavigate('tasks')} />
          ))}
        </div>
      </div>
    </div>
  );
}
