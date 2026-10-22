import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import type { PlanCreate } from '../types';
import { ArrowLeft, Loader2 } from 'lucide-react';

export default function PlanCreate() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<PlanCreate>({
    name: '',
    description: '',
    execution_mode: 'subagent',
    overview_content: '',
    tasks: [],
  });
  const [taskInputs, setTaskInputs] = useState<Array<{ title: string; description: string }>>([{ title: '', description: '' }]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const tasks = taskInputs
        .filter(t => t.title.trim())
        .map(t => ({ title: t.title.trim(), description: t.description.trim() }));

      const data: PlanCreate = {
        ...formData,
        tasks,
      };

      const plan = await api.createPlan(data);
      navigate(`/plans/${plan.id}`);
    } catch (err) {
      setError('Failed to create plan');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const addTaskInput = () => {
    setTaskInputs([...taskInputs, { title: '', description: '' }]);
  };

  const removeTaskInput = (index: number) => {
    if (taskInputs.length <= 1) return;
    setTaskInputs(taskInputs.filter((_, i) => i !== index));
  };

  const updateTaskInput = (index: number, field: 'title' | 'description', value: string) => {
    setTaskInputs(taskInputs.map((t, i) => i === index ? { ...t, [field]: value } : t));
  };

  return (
    <div className="plan-create">
      <div className="page-header">
        <button className="btn btn-ghost" onClick={() => navigate('/plans')} aria-label="Back to plans">
          <ArrowLeft size={18} aria-hidden="true" />
          Back
        </button>
        <h1>New Plan</h1>
      </div>

      {error && <div className="alert alert-error" role="alert">{error}</div>}

      <form onSubmit={handleSubmit} className="plan-form">
        <section className="form-section">
          <h2>Basic Information</h2>
          <div className="form-group">
            <label htmlFor="name">Plan Name *</label>
            <input
              id="name"
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Enter plan name"
              required
              aria-required="true"
            />
          </div>
          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Optional description"
              rows={3}
            />
          </div>
          <div className="form-group">
            <label htmlFor="execution_mode">Execution Mode</label>
            <select
              id="execution_mode"
              value={formData.execution_mode}
              onChange={(e) => setFormData({ ...formData, execution_mode: e.target.value as PlanCreate['execution_mode'] })}
            >
              <option value="subagent">Subagent (parallel subagents)</option>
              <option value="agent_team">Agent Team (Claude Code Agent Teams)</option>
              <option value="single_session">Single Session</option>
            </select>
          </div>
        </section>

        <section className="form-section">
          <h2>Overview Content (Markdown)</h2>
          <div className="form-group">
            <label htmlFor="overview_content">Overview</label>
            <textarea
              id="overview_content"
              value={formData.overview_content}
              onChange={(e) => setFormData({ ...formData, overview_content: e.target.value })}
              placeholder="# Plan Overview\n\nDescribe the plan goals, approach, and context..."
              rows={10}
              className="font-mono"
            />
          </div>
        </section>

        <section className="form-section">
          <div className="section-header">
            <h2>Initial Tasks</h2>
            <button type="button" className="btn btn-secondary btn-sm" onClick={addTaskInput}>
              Add Task
            </button>
          </div>
          {taskInputs.map((task, index) => (
            <div key={index} className="task-input-row">
              <div className="form-group task-title-group">
                <label htmlFor={`task-title-${index}`}>Task {index + 1} Title *</label>
                <input
                  id={`task-title-${index}`}
                  type="text"
                  value={task.title}
                  onChange={(e) => updateTaskInput(index, 'title', e.target.value)}
                  placeholder="Task title"
                  required={index === 0}
                  aria-required={index === 0}
                />
              </div>
              <div className="form-group task-desc-group">
                <label htmlFor={`task-desc-${index}`}>Description</label>
                <textarea
                  id={`task-desc-${index}`}
                  value={task.description}
                  onChange={(e) => updateTaskInput(index, 'description', e.target.value)}
                  placeholder="Task description"
                  rows={2}
                />
              </div>
              {taskInputs.length > 1 && (
                <button
                  type="button"
                  className="btn btn-ghost btn-sm remove-task-btn"
                  onClick={() => removeTaskInput(index)}
                  aria-label={`Remove task ${index + 1}`}
                >
                  ×
                </button>
              )}
            </div>
          ))}
        </section>

        <div className="form-actions">
          <button type="button" className="btn btn-secondary" onClick={() => navigate('/plans')}>
            Cancel
          </button>
          <button type="submit" className="btn btn-primary" disabled={loading || !formData.name.trim()}>
            {loading ? (
              <>
                <Loader2 size={18} className="spin" aria-hidden="true" />
                Creating...
              </>
            ) : (
              'Create Plan'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}