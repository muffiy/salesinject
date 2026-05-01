import { createContext, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { authenticateWithTelegram } from '../services/api';

interface AuthContextType {
  isAuthenticated: boolean;
  token: string | null;
  user: any;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  token: null,
  user: null,
  loading: true,
});

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Fallback direct access if hook is missing/not robust
  const getInitData = () => {
    return (window as any).Telegram?.WebApp?.initData || '';
  };

  useEffect(() => {
    const login = async () => {
      try {
        const initDataRaw = getInitData();
        if (initDataRaw) {
          const data = await authenticateWithTelegram(initDataRaw);
          setToken(data.access_token);
          setUser(data.user);
          localStorage.setItem('token', data.access_token);
        } else {
            // For local browser testing
            const data = await authenticateWithTelegram("mock_data=123");
            setToken(data.access_token);
            setUser(data.user);
            localStorage.setItem('token', data.access_token);
        }
      } catch (error) {
        console.error('Auth error', error);
      } finally {
        setLoading(false);
      }
    };
    login();
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated: !!token, token, user, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
