import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { api } from '../api/client';
import type { AuthTestResponse } from '../types';

interface AuthContextType {
  user: AuthTestResponse | null;
  loading: boolean;
  login: () => void;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthTestResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const response = await api.authTest();
      setUser(response);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const login = () => {
    // For OIDC PKCE flow, redirect to backend auth endpoint
    window.location.href = '/api/v1/auth/login';
  };

  const logout = async () => {
    try {
      await api.client.post('/auth/logout');
    } catch {
      // Ignore errors
    } finally {
      setUser(null);
      api.clearToken();
      window.location.href = '/';
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}