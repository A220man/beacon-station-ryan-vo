
with open('/var/lib/alan-portfolio/workspaces/ryan/beacon-station-ryan-vo/frontend/src/types/index.ts', 'r') as f:
    content = f.read()

# Update Task interface to add created_by
old_task = '''export interface Task {
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
  created_at: string;
  updated_at: string;
}'''

new_task = '''export interface Task {
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
}'''

content = content.replace(old_task, new_task)

# Update LedgerEntry interface to add created_by
old_ledger = '''export interface LedgerEntry {
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
  created_at: string;
}'''

new_ledger = '''export interface LedgerEntry {
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
}'''

content = content.replace(old_ledger, new_ledger)

with open('/var/lib/alan-portfolio/workspaces/ryan/beacon-station-ryan-vo/frontend/src/types/index.ts', 'w') as f:
    f.write(content)

print('Updated frontend types')

