import { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api/client';
import type { Plan, Task, LedgerEntry } from '../types';
import { Plus, Play, Square, Terminal, AlertCircle, CheckCircle, Clock, Loader2 } from 'lucide-react';
import { formatDistanceToNow, parseISO } from 'date-fns';

export default function PlanDetail() {
  const { id } = useParams<{ id: string }>();
  const [plan, setPlan] = useState<Plan | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [ledger, setLedger] = useState<LedgerEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'tasks' | 'ledger'>('overview');
  const [executingTaskId, setExecutingTaskId] = useState<string | null>(null);

  const loadPlan = useCallback(async () => {
    if (!id) return;
    try {
      setLoading(true);
      setError(null);
      const [planRes, tasksRes, ledgerRes] = await Promise.all([
        api.getPlan(id),
        api.listTasks(id),
        api.getLedger(id),
      ]);
      setPlan(planRes);
      setTasks(tasksRes.sort((a, b) => a.sequence - b.sequence));
      setLedger(ledgerRes);
    } catch (err) {
      setError('Failed to load plan');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadPlan();
  }, [loadPlan]);

  const handleTaskAction = async (task: Task, action: 'start' | 'complete' | 'fail') => {
    setExecutingTaskId(task.id);
    try {
      let newStatus: Task['status'];
      if (action === 'start') newStatus = 'in_progress';
      else if (action === 'complete') newStatus = 'completed';
      else newStatus = 'failed';

      await api.updateTask(id!, task.id, { status: newStatus });
      await loadPlan();
    } catch (err) {
      setError(`Failed to ${action} task`);
      console.error(err);
    } finally {
      setExecutingTaskId(null);
    }
  };

  const handleAddLedgerEntry = async (message: string, taskId?: string) => {
    try {
      await api.addLedgerEntry(id!, { message, task_id: taskId });
      const ledgerRes = await api.getLedger(id!);
      setLedger(ledgerRes);
    } catch (err) {
      setError('Failed to add log entry');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="plan-detail loading">
        <div className="spinner-large" role="status" aria-label="Loading plan" />
      </div>
    );
  }

  if (!plan) {
    return (
      <div className="plan-detail error">
        <AlertCircle size={48} aria-hidden="true" />
        <h2>Plan not found</h2>
        <p>{error || 'The requested plan does not exist'}</p>
        <Link to="/plans" className="btn btn-primary">Back to Plans</Link>
      </div>
    );
  }

  return (
    <div className="plan-detail">
      <div className="plan-header">
        <div className="plan-header-main">
          <div className="plan-title-section">
            <h1>{plan.name}</h1>
            <div className="plan-meta">
              <StatusBadge status={plan.status} />
              <span className="mode-badge">{plan.execution_mode.replace('_', ' ')}</span>
              <span className="token-estimate">~{plan.estimated_tokens.toLocaleString()} tokens</span>
            </div>
          </div>
          <div className="plan-actions">
            <Link to="/plans" className="btn btn-secondary">
              Back to Plans
            </Link>
          </div>
        </div>
        {error && <div className="alert alert-error" role="alert">{error}</div>}
      </div>

      <div className="plan-tabs" role="tablist" aria-label="Plan sections">
        <button
          role="tab"
          aria-selected={activeTab === 'overview'}
          onClick={() => setActiveTab('overview')}
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
        >
          Overview
        </button>
        <button
          role="tab"
          aria-selected={activeTab === 'tasks'}
          onClick={() => setActiveTab('tasks')}
          className={`tab-btn ${activeTab === 'tasks' ? 'active' : ''}`}
        >
          Tasks ({tasks.length})
        </button>
        <button
          role="tab"
          aria-selected={activeTab === 'ledger'}
          onClick={() => setActiveTab('ledger')}
          className={`tab-btn ${activeTab === 'ledger' ? 'active' : ''}`}
        >
          Ledger ({ledger.length})
        </button>
      </div>

      {activeTab === 'overview' && (
        <div className="tab-panel" role="tabpanel" aria-label="Overview">
          <section className="plan-overview">
            <h2>Overview</h2>
            <div className="overview-content">
              {plan.description ? (
                <p>{plan.description}</p>
              ) : (
                <p className="text-muted">No description provided</p>
              )}
            </div>

            <section className="overview-stats">
              <h3>Statistics</h3>
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-label">Total Tasks</span>
                  <span className="stat-value">{tasks.length}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Completed</span>
                  <span className="stat-value">{tasks.filter(t => t.status === 'completed').length}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">In Progress</span>
                  <span className="stat-value">{tasks.filter(t => t.status === 'in_progress').length}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Pending</span>
                  <span className="stat-value">{tasks.filter(t => t.status === 'pending').length}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Failed</span>
                  <span className="stat-value">{tasks.filter(t => t.status === 'failed').length}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Ledger Entries</span>
                  <span className="stat-value">{ledger.length}</span>
                </div>
              </div>
            </section>

            <section className="overview-timestamps">
              <h3>Timestamps</h3>
              <dl className="timestamp-list">
                <div><dt>Created</dt><dd>{formatDistanceToNow(parseISO(plan.created_at), { addSuffix: true })}</dd></div>
                <div><dt>Updated</dt><dd>{formatDistanceToNow(parseISO(plan.updated_at), { addSuffix: true })}</dd></div>
                <div><dt>Created By</dt><dd>{plan.created_by || 'Unknown'}</dd></div>
              </dl>
            </section>
          </section>
        </div>
      )}

      {activeTab === 'tasks' && (
        <div className="tab-panel" role="tabpanel" aria-label="Tasks">
          <div className="tasks-header">
            <h2>Tasks</h2>
            <button className="btn btn-primary" disabled>Add Task</button>
          </div>
          {tasks.length === 0 ? (
            <div className="empty-state">
              <Terminal size={48} aria-hidden="true" />
              <h3>No tasks yet</h3>
              <p>Tasks will appear here when added to the plan</p>
            </div>
          ) : (
            <div className="tasks-list">
              {tasks.map((task) => (
                <TaskRow
                  key={task.id}
                  task={task}
                  executing={executingTaskId === task.id}
                  onAction={handleTaskAction}
                  onAddLog={(msg) => handleAddLedgerEntry(msg, task.id)}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'ledger' && (
        <div className="tab-panel" role="tabpanel" aria-label="Ledger">
          <div className="ledger-header">
            <h2>Execution Ledger</h2>
            <button
              className="btn btn-secondary"
              onClick={() => handleAddLedgerEntry('Manual log entry')}
            >
              <Plus size={16} aria-hidden="true" /> Add Entry
            </button>
          </div>
          {ledger.length === 0 ? (
            <div className="empty-state">
              <Terminal size={48} aria-hidden="true" />
              <h3>No ledger entries</h3>
              <p>Ledger entries record task execution, test results, and commits</p>
            </div>
          ) : (
            <div className="ledger-list">
              {ledger.map((entry) => (
                <LedgerEntryRow key={entry.id} entry={entry} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function TaskRow({ task, executing, onAction, onAddLog }: {
  task: Task;
  executing: boolean;
  onAction: (task: Task, action: 'start' | 'complete' | 'fail') => void;
  onAddLog: (msg: string) => void;
}) {
  const statusConfig: Record<Task['status'], { label: string; icon: React.ReactNode; className: string }> = {
    pending: { label: 'Pending', icon: <Clock size={16} />, className: 'status-pending' },
    in_progress: { label: 'In Progress', icon: <Loader2 size={16} className="spin" />, className: 'status-in-progress' },
    completed: { label: 'Completed', icon: <CheckCircle size={16} />, className: 'status-completed' },
    failed: { label: 'Failed', icon: <AlertCircle size={16} />, className: 'status-failed' },
    skipped: { label: 'Skipped', icon: <Square size={16} />, className: 'status-skipped' },
  };

  const { label, icon, className } = statusConfig[task.status];

  return (
    <div className={`task-row ${className}`}>
      <div className="task-main">
        <div className="task-info">
          <span className="task-sequence">#{task.sequence}</span>
          <h4 className="task-title">{task.title}</h4>
          {task.description && <p className="task-description">{task.description}</p>}
        </div>
        <div className="task-status">
          <span className={`task-status-badge ${className}`}>
            {icon} {label}
          </span>
        </div>
      </div>
      <div className="task-actions">
        {task.status === 'pending' && (
          <button
            className="btn btn-sm btn-primary"
            onClick={() => onAction(task, 'start')}
            disabled={executing}
            aria-label={`Start ${task.title}`}
          >
            <Play size={14} aria-hidden="true" /> Start
          </button>
        )}
        {task.status === 'in_progress' && (
          <>
            <button
              className="btn btn-sm btn-success"
              onClick={() => onAction(task, 'complete')}
              disabled={executing}
              aria-label={`Complete ${task.title}`}
            >
              <CheckCircle size={14} aria-hidden="true" /> Complete
            </button>
            <button
              className="btn btn-sm btn-error"
              onClick={() => onAction(task, 'fail')}
              disabled={executing}
              aria-label={`Mark ${task.title} as failed`}
            >
              <AlertCircle size={14} aria-hidden="true" /> Fail
            </button>
          </>
        )}
        {task.status === 'completed' && (
          <button
            className="btn btn-sm btn-secondary"
            onClick={() => onAction(task, 'start')}
            disabled={executing}
            aria-label={`Restart ${task.title}`}
          >
            <Loader2 size={14} aria-hidden="true" /> Restart
          </button>
        )}
        <button
          className="btn btn-sm btn-ghost"
          onClick={() => onAddLog(`Task ${task.sequence}: ${task.title} - status changed to ${task.status}`)}
          aria-label={`Add log for ${task.title}`}
        >
          <Terminal size={14} aria-hidden="true" /> Log
        </button>
      </div>
    </div>
  );
}

function LedgerEntryRow({ entry }: { entry: LedgerEntry }) {
  return (
    <div className="ledger-entry">
      <div className="ledger-entry-header">
        <span className="ledger-sequence">#{entry.sequence}</span>
        <time className="ledger-time" dateTime={entry.created_at}>
          {formatDistanceToNow(parseISO(entry.created_at), { addSuffix: true })}
        </time>
      </div>
      <p className="ledger-message">{entry.message}</p>
      {entry.test_command && (
        <div className="ledger-test">
          <code>{entry.test_command}</code>
          {entry.test_result && <span className="ledger-result">→ {entry.test_result}</span>}
          {entry.exit_code !== null && (
            <span className={`ledger-exit ${entry.exit_code === 0 ? 'success' : 'fail'}`}>
              exit {entry.exit_code}
            </span>
          )}
        </div>
      )}
      {entry.commits_range && (
        <div className="ledger-commits">
          <code>{entry.commits_range}</code>
        </div>
      )}
      {entry.tokens_used > 0 && (
        <div className="ledger-tokens">
          <span>Tokens: {entry.tokens_used.toLocaleString()}</span>
        </div>
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