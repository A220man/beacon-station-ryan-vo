import { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { Loader2, Shield, AlertCircle } from 'lucide-react';

export default function Login() {
  const { login, loading: authLoading, user } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    if (!authLoading) {
      setChecking(false);
    }
  }, [authLoading]);

  const handleLogin = () => {
    setError(null);
    login();
  };

  if (checking) {
    return (
      <div className="login-page checking">
        <div className="spinner-large" role="status" aria-label="Checking authentication" />
      </div>
    );
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-header">
          <div className="login-icon">
            <Shield size={48} aria-hidden="true" />
          </div>
          <h1>Beacon Station</h1>
          <p className="text-muted">Agentic skills framework & methodology</p>
        </div>

        {error && (
          <div className="alert alert-error" role="alert">
            <AlertCircle size={18} aria-hidden="true" />
            {error}
          </div>
        )}

        <div className="login-info">
          <h3>Sign in with Keycloak</h3>
          <p>This application uses OIDC authentication via Keycloak with PKCE.</p>
          <ul>
            <li>Secure authorization code flow with PKCE</li>
            <li>HttpOnly cookies for session management</li>
            <li>Role-based access control (viewer/operator/admin)</li>
          </ul>
        </div>

        <button
          className="btn btn-primary btn-block btn-lg"
          onClick={handleLogin}
          disabled={authLoading}
        >
          {authLoading ? (
            <>
              <Loader2 size={20} className="spin" aria-hidden="true" />
              Redirecting...
            </>
          ) : (
            'Sign in with Keycloak'
          )}
        </button>

        <div className="login-footer">
          <p className="text-muted">
            Demo mode: {(user as any)?.demo_mode ? 'Enabled' : 'Disabled'}
          </p>
        </div>
      </div>
    </div>
  );
}