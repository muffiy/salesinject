import { createContext, useContext, useRef, useCallback } from 'react';
import type { ReactNode } from 'react';
import api from '../services/api';

// ── Types ─────────────────────────────────────────────────────────────────────
interface AuthContextValue {
  getToken: () => string | null;
  setToken: (token: string) => void;
  clearToken: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

// ── Provider ──────────────────────────────────────────────────────────────────
export function AuthProvider({ children }: { children: ReactNode }) {
  // Token lives in a ref — survives re-renders, never touches localStorage.
  const tokenRef = useRef<string | null>(null);

  const getToken = useCallback(() => tokenRef.current, []);

  const setToken = useCallback((token: string) => {
    tokenRef.current = token;
    // Inject into every future axios request immediately
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }, []);

  const clearToken = useCallback(() => {
    tokenRef.current = null;
    delete api.defaults.headers.common['Authorization'];
  }, []);

  return (
    <AuthContext.Provider value={{ getToken, setToken, clearToken }}>
      {children}
    </AuthContext.Provider>
  );
}

// ── Hook ──────────────────────────────────────────────────────────────────────
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
