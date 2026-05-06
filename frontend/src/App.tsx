import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import MissionFeed from './pages/MissionFeed';
import ActiveMission from './pages/ActiveMission';
import IntelHub from './pages/IntelHub';
import LoopEngine from './pages/LoopEngine';
import { MapPage } from './pages/MapPage';
import SplashScreen from './components/SplashScreen';
import PermissionGate from './components/PermissionGate';
import BottomNavigation from './components/BottomNavigation';
import LiveTicker from './components/LiveTicker';
import { AuthProvider } from './context/AuthContext';

// Layout component that wraps pages with bottom navigation
function MainLayout({ children }: { children: React.ReactNode }) {
  const location = useLocation();

  // Don't show navigation on these pages
  const hideNavigation = [
    '/mission/', // Active mission (full screen)
    '/replay/', // Loop engine (full screen replay)
  ].some(path => location.pathname.startsWith(path));

  // Check if user has an active mission (simplified)
  const hasActiveMission = location.pathname.startsWith('/mission/');

  return (
    <>
      <div style={{
        paddingBottom: hideNavigation ? '0' : '80px',
        paddingTop: '24px',
        minHeight: '100vh',
        background: 'var(--war-black)',
      }}>
        {children}
      </div>
      <LiveTicker />
      {!hideNavigation && <BottomNavigation hasActiveMission={hasActiveMission} />}
    </>
  );
}

function App() {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasPermissions, setHasPermissions] = useState(false);

  // For development, bypass splash and permissions
  useEffect(() => {
    if (import.meta.env.DEV) {
      setIsLoaded(true);
      setHasPermissions(true);
    }
  }, []);

  if (!isLoaded) return <SplashScreen onFinish={() => setIsLoaded(true)} />;
  if (!hasPermissions) return <PermissionGate onGrant={() => setHasPermissions(true)} />;

  return (
    <AuthProvider>
      <BrowserRouter>
        <MainLayout>
          <Routes>
            <Route path="/" element={<MissionFeed />} />
            <Route path="/mission/:offerId" element={<ActiveMission />} />
            <Route path="/intel" element={<IntelHub />} />
            <Route path="/map" element={<MapPage />} />
            <Route path="/replay/:traceId" element={<LoopEngine />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </MainLayout>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;