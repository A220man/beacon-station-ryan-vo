import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider, useAuth } from './hooks/useAuth';
import App from './App';

// Mock the API client
vi.mock('./api/client', () => ({
  api: {
    authTest: vi.fn(),
    health: vi.fn(),
    listPlans: vi.fn(),
  },
}));

import { api } from './api/client';

const mockAuthTest = api.authTest as ReturnType<typeof vi.fn>;
const mockHealth = api.health as ReturnType<typeof vi.fn>;
const mockListPlans = api.listPlans as ReturnType<typeof vi.fn>;

function renderApp() {
  return render(
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  );
}

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockAuthTest.mockResolvedValue({ authenticated: true, user_id: '1', email: 'test@example.com', roles: ['viewer'] });
    mockHealth.mockResolvedValue({ status: 'ok', version: '1.0.0', environment: 'development', database: 'connected', oidc_configured: true, demo_mode: false });
    mockListPlans.mockResolvedValue({ plans: [], total: 0, limit: 10, offset: 0 });
  });

  it('renders dashboard when authenticated', async () => {
    renderApp();
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Dashboard', level: 1 })).toBeInTheDocument();
    });
  });

  it('shows loading state initially', () => {
    let resolveAuth: (value: any) => void;
    const authPromise = new Promise(resolve => { resolveAuth = resolve; });
    mockAuthTest.mockImplementation(() => authPromise);
    renderApp();
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    resolveAuth!({ authenticated: true, user_id: '1', email: 'test@example.com', roles: ['viewer'] });
  });

  it('redirects to login when not authenticated', async () => {
    mockAuthTest.mockResolvedValue({ authenticated: false, roles: [] });
    renderApp();
    await waitFor(() => {
      expect(window.location.pathname).toBe('/login');
    });
  });
});

describe('useAuth', () => {
  it('provides user and loading state', async () => {
    mockAuthTest.mockResolvedValue({ authenticated: true, user_id: '1', email: 'test@example.com', roles: ['viewer'] });

    function TestComponent() {
      const { user, loading } = useAuth();
      return <div data-testid="auth">{loading ? 'loading' : (user?.authenticated ? 'authenticated' : 'unauthenticated')}</div>;
    }

    render(
      <BrowserRouter>
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      </BrowserRouter>
    );

    expect(screen.getByTestId('auth')).toHaveTextContent('loading');

    await waitFor(() => {
      expect(screen.getByTestId('auth')).toHaveTextContent('authenticated');
    });
  });
});