import { useAuth } from '../hooks/useAuth';
import { User, Shield, Database, Key, Save } from 'lucide-react';

export default function Settings() {
  const { user } = useAuth();

  return (
    <div className="settings">
      <h1>Settings</h1>

      <section className="settings-section">
        <h2>Account</h2>
        <div className="settings-card">
          <div className="setting-row">
            <div className="setting-label">
              <User size={20} aria-hidden="true" />
              <span>Email</span>
            </div>
            <div className="setting-value">{user?.email || 'Not available'}</div>
          </div>
          <div className="setting-row">
            <div className="setting-label">
              <Shield size={20} aria-hidden="true" />
              <span>Roles</span>
            </div>
            <div className="setting-value">
              {user?.roles?.map(r => <span key={r} className="role-badge">{r}</span>).join(' ') || 'viewer'}
            </div>
          </div>
          <div className="setting-row">
            <div className="setting-label">
              <Key size={20} aria-hidden="true" />
              <span>User ID</span>
            </div>
            <div className="setting-value font-mono">{user?.user_id || 'Not available'}</div>
          </div>
        </div>
      </section>

      <section className="settings-section">
        <h2>System</h2>
        <div className="settings-card">
          <div className="setting-row">
            <div className="setting-label">
              <Database size={20} aria-hidden="true" />
              <span>Database</span>
            </div>
            <div className="setting-value">
              <span className="status-badge status-active">Connected</span>
            </div>
          </div>
          <div className="setting-row">
            <div className="setting-label">
              <Shield size={20} aria-hidden="true" />
              <span>OIDC Configured</span>
            </div>
            <div className="setting-value">
              <span className="status-badge status-active">Yes</span>
            </div>
          </div>
          <div className="setting-row">
            <div className="setting-label">
              <Key size={20} aria-hidden="true" />
              <span>Demo Mode</span>
            </div>
            <div className="setting-value">
              <span className={`status-badge ${(user as any)?.demo_mode ? 'status-warning' : 'status-active'}`}>
                {(user as any)?.demo_mode ? 'Enabled (Local Only)' : 'Disabled'}
              </span>
            </div>
          </div>
        </div>
      </section>

      <section className="settings-section">
        <h2>Preferences</h2>
        <div className="settings-card">
          <div className="setting-row">
            <div className="setting-label">
              <span>Theme</span>
            </div>
            <div className="setting-value">
              <select className="setting-select" defaultValue="system">
                <option value="system">System</option>
                <option value="dark">Dark</option>
                <option value="light">Light</option>
              </select>
            </div>
          </div>
          <div className="setting-row">
            <div className="setting-label">
              <span>Auto-refresh Interval</span>
            </div>
            <div className="setting-value">
              <select className="setting-select" defaultValue="30">
                <option value="10">10 seconds</option>
                <option value="30">30 seconds</option>
                <option value="60">1 minute</option>
                <option value="300">5 minutes</option>
                <option value="0">Disabled</option>
              </select>
            </div>
          </div>
        </div>
        <div className="settings-actions">
          <button className="btn btn-primary" disabled>
            <Save size={18} aria-hidden="true" />
            Save Preferences
          </button>
        </div>
      </section>
    </div>
  );
}