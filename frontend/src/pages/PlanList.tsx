import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import type { Plan, PlanListResponse } from '../types';
import { Search, Filter, Plus, ChevronLeft, ChevronRight, FileText } from 'lucide-react';
import { formatDistanceToNow, parseISO } from 'date-fns';

export default function PlanList() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const pageSize = 10;

  const loadPlans = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res: PlanListResponse = await api.listPlans(pageSize, (page - 1) * pageSize, statusFilter === 'all' ? undefined : statusFilter);
      setPlans(res.plans);
      setTotal(res.total);
    } catch (err) {
      setError('Failed to load plans');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [page, statusFilter]);

  useEffect(() => {
    loadPlans();
  }, [loadPlans]);

  const filteredPlans = plans.filter(plan =>
    plan.name.toLowerCase().includes(search.toLowerCase())
  );

  const totalPages = Math.ceil(total / pageSize);

  if (loading && plans.length === 0) {
    return (
      <div className="plan-list loading">
        <div className="spinner-large" role="status" aria-label="Loading plans" />
      </div>
    );
  }

  return (
    <div className="plan-list">
      <div className="page-header">
        <h1>Plans</h1>
        <Link to="/plans/new" className="btn btn-primary">
          <Plus size={18} aria-hidden="true" />
          New Plan
        </Link>
      </div>

      {error && <div className="alert alert-error" role="alert">{error}</div>}

      <div className="plan-filters">
        <div className="search-box">
          <Search size={18} aria-hidden="true" />
          <input
            type="search"
            placeholder="Search plans..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search plans"
          />
        </div>
        <div className="filter-box">
          <Filter size={18} aria-hidden="true" />
          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            aria-label="Filter by status"
          >
            <option value="all">All Status</option>
            <option value="draft">Draft</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
            <option value="archived">Archived</option>
          </select>
        </div>
      </div>

      {filteredPlans.length === 0 ? (
        <div className="empty-state">
          <FileText size={48} aria-hidden="true" />
          <h3>{search || statusFilter !== 'all' ? 'No matching plans' : 'No plans yet'}</h3>
          <p>{search || statusFilter !== 'all' ? 'Try adjusting your filters' : 'Create your first plan to get started'}</p>
          {(search || statusFilter !== 'all') && (
            <button onClick={() => { setSearch(''); setStatusFilter('all'); }} className="btn btn-secondary">
              Clear Filters
            </button>
          )}
          {!search && statusFilter === 'all' && (
            <Link to="/plans/new" className="btn btn-primary">
              <Plus size={18} aria-hidden="true" />
              Create Plan
            </Link>
          )}
        </div>
      ) : (
        <>
          <div className="plan-table-container">
            <table className="plan-table" role="table">
              <thead>
                <tr>
                  <th scope="col">Name</th>
                  <th scope="col">Description</th>
                  <th scope="col">Status</th>
                  <th scope="col">Mode</th>
                  <th scope="col">Est. Tokens</th>
                  <th scope="col">Created</th>
                  <th scope="col">Updated</th>
                  <th scope="col"></th>
                </tr>
              </thead>
              <tbody>
                {filteredPlans.map((plan) => (
                  <tr key={plan.id}>
                    <td>
                      <Link to={`/plans/${plan.id}`} className="plan-name-link">
                        {plan.name}
                      </Link>
                    </td>
                    <td className="plan-description">{plan.description || '—'}</td>
                    <td><StatusBadge status={plan.status} /></td>
                    <td><span className="mode-badge">{plan.execution_mode.replace('_', ' ')}</span></td>
                    <td>{plan.estimated_tokens.toLocaleString()}</td>
                    <td>{formatDistanceToNow(parseISO(plan.created_at), { addSuffix: true })}</td>
                    <td>{formatDistanceToNow(parseISO(plan.updated_at), { addSuffix: true })}</td>
                    <td>
                      <div className="action-buttons">
                        <Link to={`/plans/${plan.id}`} className="btn btn-sm btn-ghost" aria-label={`View ${plan.name}`}>
                          View
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <nav className="pagination" aria-label="Pagination">
              <button
                className="btn btn-sm btn-secondary"
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                aria-label="Previous page"
              >
                <ChevronLeft size={16} aria-hidden="true" />
              </button>
              <span className="pagination-info" aria-live="polite">
                Page {page} of {totalPages} ({total} total)
              </span>
              <button
                className="btn btn-sm btn-secondary"
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                aria-label="Next page"
              >
                <ChevronRight size={16} aria-hidden="true" />
              </button>
            </nav>
          )}
        </>
      )}
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