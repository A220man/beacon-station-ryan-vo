export interface Plan {
  id: string;
  name: string;
  description: string | null;
  execution_mode: 'subagent' | 'agent_team' | 'single_session';
  status: 'draft' | 'active' | 'completed' | 'archived';
  overview_path: string;
  tasks_dir: string;
  estimated_tokens: number;
  created_at: string;
  updated_at: string;
  created_by: string | null;
  tasks?: Task[];
  ledger_entries?: LedgerEntry[];
}

export interface Task {
  id: string;
  plan_id: string;
  sequence: number;
  title: string;
  description: string | null;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'skipped';
  file_path: string | null;
  file_content: string | null;
  estimated_tokens: number;
  started_at: string | null;
  completed_at: string | null;
  created_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface LedgerEntry {
  id: string;
  plan_id: string;
  task_id: string | null;
  sequence: number;
  message: string;
  commits_range: string | null;
  test_command: string | null;
  test_result: string | null;
  exit_code: number | null;
  tokens_used: number;
  meta: Record<string, unknown>;
  created_by: string | null;
  created_at: string;
}

export interface PlanListResponse {
  plans: Plan[];
  total: number;
  limit: number;
  offset: number;
}

export interface PlanCreate {
  name: string;
  description?: string;
  execution_mode?: 'subagent' | 'agent_team' | 'single_session';
  overview_content?: string;
  tasks?: Array<{ title: string; description?: string }>;
}

export interface PlanUpdate {
  name?: string;
  description?: string;
  status?: 'draft' | 'active' | 'completed' | 'archived';
  overview_content?: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  sequence?: number;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: 'pending' | 'in_progress' | 'completed' | 'failed' | 'skipped';
  file_content?: string;
}

export interface LedgerEntryCreate {
  message: string;
  task_id?: string;
  commits_range?: string;
  test_command?: string;
  test_result?: string;
  exit_code?: number;
  tokens_used?: number;
  meta?: Record<string, unknown>;
}

export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
  database: string;
  oidc_configured: boolean;
  demo_mode: boolean;
}

export interface AuthTestResponse {
  authenticated: boolean;
  user_id?: string;
  email?: string;
  roles: string[];
}

export interface TokenEstimateResponse {
  plan_id: string;
  estimated_tokens: number;
  breakdown: {
    overview: number;
    tasks: number;
    ledger: number;
  };
}