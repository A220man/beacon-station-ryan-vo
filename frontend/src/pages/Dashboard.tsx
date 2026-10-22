import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import type { Plan, HealthResponse } from '../types';
import { TrendingUp, FileText, Clock, AlertCircle, CheckCircle, Plus } from 'lucide-react';
import { formatDistanceToNow, parseISO } from 'date-fns';

export default function Dashboard() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      const [plansRes, healthRes] = await Promise.all([
        api.listPlans(5, 0),
        api.health(),
      ]);
      setPlans(plansRes.plans);
      setHealth(healthRes);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="dashboard loading">
        <div className="spinner-large" role="status" aria-label="Loading dashboard" />
      </div>
    );
  }

  const activePlans = plans.filter(p => p.status === 'active').length;
  const completedPlans = plans.filter(p => p.status === 'completed').length;
  const draftPlans = plans.filter(p => p.status === 'draft').length;

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <Link to="/plans/new" className="btn btn-primary">
          <Plus size={18} aria-hidden="true" />
          New Plan
        </Link>
      </div>

      {error && <div className="alert alert-error" role="alert">{error}</div>}

      <section className="stats-grid" aria-labelledby="stats-heading">
        <h2 id="stats-heading" className="sr-only">Statistics</h2>
        <div className="stat-card">
          <div className="stat-icon">
            <FileText size={24} aria-hidden="true" />
          </div>
          <div className="stat-content">
            <p className="stat-value">{plans.length}</p>
            <p className="stat-label">Total Plans</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon success">
            <CheckCircle size={24} aria-hidden="true" />
          </div>
          <div className="stat-content">
            <p className="stat-value">{activePlans}</p>
            <p className="stat-label">Active</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon completed">
            <TrendingUp size={24} aria-hidden="true" />
          </div>
          <div className="stat-content">
            <p className="stat-value">{completedPlans}</p>
            <p className="stat-label">Completed</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon warning">
            <Clock size={24} aria-hidden="true" />
          </div>
          <div className="stat-content">
            <p className="stat-value">{draftPlans}</p>
            <p className="stat-label">Draft</p>
          </div>
        </div>
      </section>

      <section className="recent-plans" aria-labelledby="recent-heading">
        <div className="section-header">
          <h2 id="recent-heading">Recent Plans</h2>
          <Link to="/plans" className="btn btn-ghost">View All</Link>
        </div>
        {plans.length === 0 ? (
          <div className="empty-state">
            <FileText size={48} aria-hidden="true" />
            <h3>No plans yet</h3>
            <p>Create your first plan to get started</p>
            <Link to="/plans/new" className="btn btn-primary">
              <Plus size={18} aria-hidden="true" />
              Create Plan
            </Link>
          </div>
        ) : (
          <div className="plan-table-container">
            <table className="plan-table" role="table">
              <thead>
                <tr>
                  <th scope="col">Name</th>
                  <th scope="col">Status</th>
                  <th scope="col">Mode</th>
                  <th scope="col">Est. Tokens</th>
                  <th scope="col">Updated</th>
                  <th scope="col"></th>
                </tr>
              </thead>
              <tbody>
                {plans.map((plan) => (
                  <tr key={plan.id}>
                    <td>
                      <Link to={`/plans/${plan.id}`} className="plan-name-link">
                        {plan.name}
                      </Link>
                    </td>
                    <td>
                      <StatusBadge status={plan.status} />
                    </td>
                    <td>
                      <span className="mode-badge">{plan.execution_mode.replace('_', ' ')}</span>
                    </td>
                    <td>{plan.estimated_tokens.toLocaleString()}</td>
                    <td>{formatDistanceToNow(parseISO(plan.updated_at), { addSuffix: true })}</td>
                    <td>
                      <Link to={`/plans/${plan.id}`} className="btn btn-sm btn-ghost" aria-label={`View ${plan.name}`}>
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

      </section>

      <section className="system-health" aria-labelledby="health-heading">
        <h2 id="health-heading">System Health</h2>
        <div className="health-grid">
          <div className="health-item">
            <span className={`health-status ${health?.database === 'connected' ? 'healthy' : 'unhealthy'}`}>
              {health?.database === 'connected' ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
            </span>
            <span>Database: {health?.database || 'Unknown'}</span>
          </div>
          <div className="health-item">
            <span className={`health-status ${health?.oidc_configured ? 'healthy' : 'warning'}`}>
              {health?.oidc_configured ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
            </span>
            <span>OIDC: {health?.oidc_configured ? 'Configured' : 'Not configured'}</span>
          </div>
          <div className="health-item">
            <span className="health-status healthy"><CheckCircle size={16} /></span>
            <span>Environment: {health?.environment || 'Unknown'}</span>
          </div>
          <div className="health-item">
            <span className={`health-status ${health?.demo_mode ? 'warning' : 'healthy'}`}>
              {health?.demo_mode ? <AlertCircle size={16} /> : <CheckCircle size={16} />}
            </span>
            <span>Demo Mode: {health?.demo_mode ? 'Enabled' : 'Disabled'}</span>
          </div>
        </div>
      </section>
    </div>
  );
}

function StatusBadge({ status }: { status: Plan['status'] }) {
  const config: Record<Plan['status'], { label: string; className: string }> = {
    draft: { label: 'Draft', className: 'status-draft' },
    active: { label: 'Active', className: 'status-active' },
    completed: { label: 'Completed', className: 'status-completed' },
    archived: { label: 'Archived', className: 'status-archived' },
  };
  const { label, className } = config[status];
  return <span className={`status-badge ${className}`}>{label}</span>;
}