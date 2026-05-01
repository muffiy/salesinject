import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Landing from './pages/Landing';
import MapPage from './pages/MapPage';
import Dashboard from './pages/Dashboard';

const PrivateRoute = ({ children }: { children: JSX.Element }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) return <div className="h-screen w-screen flex items-center justify-center bg-[var(--war-black)] text-white">Loading...</div>;
  if (!isAuthenticated) return <Navigate to="/" />;
  
  return children;
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/app/*" element={
            <PrivateRoute>
              <Routes>
                <Route path="map" element={<MapPage />} />
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="*" element={<Navigate to="map" />} />
              </Routes>
            </PrivateRoute>
          } />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
