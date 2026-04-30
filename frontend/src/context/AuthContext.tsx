import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useInitData } from '@telegram-apps/sdk-react';
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
  const initData = useInitData();

  useEffect(() => {
    const login = async () => {
      try {
        if (initData && initData.raw) {
          const data = await authenticateWithTelegram(initData.raw);
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
  }, [initData]);

  return (
    <AuthContext.Provider value={{ isAuthenticated: !!token, token, user, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
