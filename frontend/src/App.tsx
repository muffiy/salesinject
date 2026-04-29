import { useEffect, useState } from 'react';
import { useTelegramUser } from './hooks/useTelegramUser';
import { authenticate, refreshToken } from './services/api';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Dashboard } from './pages/Dashboard';
import { Tasks } from './pages/Tasks';
import { Agents } from './pages/Agents';
import { Profile } from './pages/Profile';
import { MapPage } from './pages/MapPage';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { TelegramGuard } from './guards/TelegramGuard';
import { Landing } from './pages/Landing';
import { Onboarding } from './pages/Onboarding';
import { PaperclipSidebar } from './pages/PaperclipSidebar';
import { getPaperclips } from './services/api';

type Tab = 'dashboard' | 'tasks' | 'agents' | 'profile' | 'map' | 'paperclip';

// Token expires in 30 min; refresh silently every 28 min
const REFRESH_INTERVAL_MS = 28 * 60 * 1000;

function LoadingScreen() {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100dvh',
      gap: '16px',
      background: 'var(--si-bg)',
    }}>
      <div style={{
        width: '64px', height: '64px', borderRadius: '20px',
        background: 'linear-gradient(135deg, var(--si-accent), var(--si-accent-2))',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '32px',
        boxShadow: '0 0 32px rgba(108,99,255,0.4)',
      }}>
        ⚡
      </div>
      <div style={{ fontSize: '20px', fontWeight: '800' }}>SalesInject</div>
      <div style={{ fontSize: '13px', color: 'var(--si-muted)' }}>Loading your workspace...</div>
    </div>
  );
}

function ErrorScreen({ message }: { message: string }) {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'center', height: '100dvh', gap: '12px', padding: '24px',
    }}>
      <div style={{ fontSize: '40px' }}>⚠️</div>
      <div style={{ fontWeight: '700', fontSize: '16px' }}>Something went wrong</div>
      <div style={{ color: 'var(--si-muted)', textAlign: 'center', fontSize: '13px' }}>{message}</div>
    </div>
  );
}

/** Inner component — has access to AuthContext. */
function AppShell() {
  const { setToken } = useAuth();
  const { user, initData } = useTelegramUser();
  const [tab, setTab] = useState<Tab>('dashboard');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [hasUnreadIntel, setHasUnreadIntel] = useState(false);

  // Check for unread intel logic
  const checkUnreadIntel = async () => {
    try {
      const items = await getPaperclips();
      if (items.length > 0) {
        const lastViewed = localStorage.getItem('salesinject_last_viewed_paperclips');
        if (!lastViewed || new Date(items[0].created_at) > new Date(lastViewed)) {
          setHasUnreadIntel(true);
        } else {
          setHasUnreadIntel(false);
        }
      }
    } catch (e) {
      // safe ignore
    }
  };

  useEffect(() => {
    // Listen for custom events to clear or refresh badge
    const onIntelViewed = () => setHasUnreadIntel(false);
    window.addEventListener('paperclipsViewed', onIntelViewed);
    // Poll for unread intel every 30 seconds
    const intelInterval = setInterval(checkUnreadIntel, 30000);
    
    return () => {
      window.removeEventListener('paperclipsViewed', onIntelViewed);
      clearInterval(intelInterval);
    };
  }, []);

  useEffect(() => {
    if (initData) {
      authenticate(initData)
        .then((token) => {
          setToken(token);
          setLoading(false);
          checkUnreadIntel(); // Initial check on auth
        })
        .catch((err) => {
          console.error('Auth failed', err);
          setError('Authentication failed. Please re-open from Telegram.');
          setLoading(false);
        });
    } else if (import.meta.env.DEV) {
      console.log('Dev mode: no Telegram context, skipping auth.');
      setLoading(false);
    } else {
      setError('Please open this app through Telegram.');
      setLoading(false);
    }
  }, [initData, setToken]);

  useEffect(() => {
    if (loading || error) return;
    const interval = setInterval(() => {
      refreshToken()
        .then((token) => setToken(token))
        .catch(() => console.warn('Token refresh failed — user may need to re-authenticate.'));
    }, REFRESH_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [loading, error, setToken]);

  if (loading) return <LoadingScreen />;
  if (error) return <ErrorScreen message={error} />;

  const renderSidebarPage = () => {
    switch (tab) {
      case 'dashboard': return <Dashboard user={user} onNavigate={(t) => setTab(t as Tab)} />;
      case 'tasks':     return <Tasks />;
      case 'agents':    return <Agents />;
      case 'profile':   return <Profile user={user} />;
      case 'paperclip': return <PaperclipSidebar />;
      default:          return <Dashboard user={user} onNavigate={(t) => setTab(t as Tab)} />;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100dvh', overflow: 'hidden', background: 'var(--war-black)' }}>
      {/* Top Paperclip-style Navigation */}
      <header style={{ height: '64px', borderBottom: '1px solid var(--war-gray-700)', display: 'flex', alignItems: 'center', padding: '0 24px', background: 'var(--si-surface)', zIndex: 10 }}>
        <div style={{ fontFamily: 'var(--font-display)', fontSize: '20px', fontWeight: '900', color: 'var(--war-cyan)' }}>SALES<span style={{ color: 'white' }}>INJECT</span></div>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: '32px' }}>
          <button onClick={() => setTab('dashboard')} style={{ background: 'none', border: 'none', color: tab === 'dashboard' ? 'var(--war-cyan)' : 'var(--si-muted)', cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: '13px', fontWeight: '700' }}>COMMAND</button>
          
          <div style={{ position: 'relative', display: 'flex' }}>
            <button onClick={() => setTab('paperclip')} style={{ background: 'none', border: 'none', color: tab === 'paperclip' ? 'var(--war-cyan)' : 'var(--si-muted)', cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: '13px', fontWeight: '700' }}>
              PAPERCLIP
            </button>
            {hasUnreadIntel && (
              <span style={{ position: 'absolute', top: '-4px', right: '-12px', width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--war-red)', boxShadow: '0 0 10px var(--war-red)' }} />
            )}
          </div>
          
          <button onClick={() => setTab('agents')} style={{ background: 'none', border: 'none', color: tab === 'agents' ? 'var(--war-cyan)' : 'var(--si-muted)', cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: '13px', fontWeight: '700' }}>AGENTS</button>
          <button onClick={() => setTab('tasks')} style={{ background: 'none', border: 'none', color: tab === 'tasks' ? 'var(--war-cyan)' : 'var(--si-muted)', cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: '13px', fontWeight: '700' }}>TICKETS</button>
          <button onClick={() => setTab('profile')} style={{ background: 'none', border: 'none', color: tab === 'profile' ? 'var(--war-cyan)' : 'var(--si-muted)', cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: '13px', fontWeight: '700' }}>PROFILE</button>
        </div>
      </header>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* WorldMonitor Map Area (Always visible) */}
        <div style={{ flex: 1, position: 'relative' }}>
          <MapPage />
        </div>

        {/* Paperclip Task/Agent Sidebar */}
        <div style={{ width: '450px', background: 'var(--si-surface)', borderLeft: '1px solid var(--war-gray-700)', display: 'flex', flexDirection: 'column', zIndex: 10, overflowY: 'auto' }}>
           {renderSidebarPage()}
        </div>
      </div>
    </div>
  );
}

/** Root — wraps everything in AuthProvider so token is available app-wide. */
export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route element={<TelegramGuard />}>
            <Route path="/app" element={<AppShell />} />
            <Route path="/onboarding" element={<Onboarding />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
