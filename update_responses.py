
with open('/var/lib/alan-portfolio/workspaces/ryan/beacon-station-ryan-vo/backend/app/api/plans.py', 'r') as f:
    content = f.read()

# Update PlanResponse to add created_by
old_plan_response = '''class PlanResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: PlanStatus
    execution_mode: ExecutionMode
    overview_path: str
    tasks_dir: str
    estimated_tokens: int
    actual_tokens: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    task_count: int
    completed_task_count: int

    @classmethod
    def from_orm(cls, plan: Plan) -> "PlanResponse":
        completed = sum(1 for t in plan.tasks if t.status == TaskStatus.COMPLETED)
        return cls(
            id=plan.id,
            name=plan.name,
            description=plan.description,
            status=plan.status,
            execution_mode=plan.execution_mode,
            overview_path=plan.overview_path,
            tasks_dir=plan.tasks_dir,
            estimated_tokens=plan.estimated_tokens,
            actual_tokens=plan.actual_tokens,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
            completed_at=plan.completed_at,
            task_count=len(plan.tasks),
            completed_task_count=completed,
        )'''

new_plan_response = '''class PlanResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: PlanStatus
    execution_mode: ExecutionMode
    overview_path: str
    tasks_dir: str
    estimated_tokens: int
    actual_tokens: int
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    task_count: int
    completed_task_count: int

    @classmethod
    def from_orm(cls, plan: Plan) -> "PlanResponse":
        completed = sum(1 for t in plan.tasks if t.status == TaskStatus.COMPLETED)
        return cls(
            id=plan.id,
            name=plan.name,
            description=plan.description,
            status=plan.status,
            execution_mode=plan.execution_mode,
            overview_path=plan.overview_path,
            tasks_dir=plan.tasks_dir,
            estimated_tokens=plan.estimated_tokens,
            actual_tokens=plan.actual_tokens,
            created_by=plan.created_by,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
            completed_at=plan.completed_at,
            task_count=len(plan.tasks),
            completed_task_count=completed,
        )'''

content = content.replace(old_plan_response, new_plan_response)

# Update TaskResponse to add created_by
old_task_response = '''class TaskResponse(BaseModel):
    id: str
    plan_id: str
    sequence: int
    title: str
    description: Optional[str]
    file_path: str
    status: TaskStatus
    assigned_to: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_tokens: int
    actual_tokens: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, task: Task) -> "TaskResponse":
        return cls(
            id=task.id,
            plan_id=task.plan_id,
            sequence=task.sequence,
            title=task.title,
            description=task.description,
            file_path=task.file_path,
            status=task.status,
            assigned_to=task.assigned_to,
            started_at=task.started_at,
            completed_at=task.completed_at,
            estimated_tokens=task.estimated_tokens,
            actual_tokens=task.actual_tokens,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )'''

new_task_response = '''class TaskResponse(BaseModel):
    id: str
    plan_id: str
    sequence: int
    title: str
    description: Optional[str]
    file_path: str
    status: TaskStatus
    assigned_to: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_tokens: int
    actual_tokens: int
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, task: Task) -> "TaskResponse":
        return cls(
            id=task.id,
            plan_id=task.plan_id,
            sequence=task.sequence,
            title=task.title,
            description=task.description,
            file_path=task.file_path,
            status=task.status,
            assigned_to=task.assigned_to,
            started_at=task.started_at,
            completed_at=task.completed_at,
            estimated_tokens=task.estimated_tokens,
            actual_tokens=task.actual_tokens,
            created_by=task.created_by,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )'''

content = content.replace(old_task_response, new_task_response)

# Update LedgerEntryResponse to add created_by
old_ledger_response = '''class LedgerEntryResponse(BaseModel):
    id: str
    plan_id: str
    task_id: Optional[str]
    sequence: int
    message: str
    commits_range: Optional[str]
    test_command: Optional[str]
    test_result: Optional[str]
    exit_code: Optional[int]
    tokens_used: int
    meta: dict
    created_at: datetime

    @classmethod
    def from_orm(cls, entry: LedgerEntry) -> "LedgerEntryResponse":
        return cls(
            id=entry.id,
            plan_id=entry.plan_id,
            task_id=entry.task_id,
            sequence=entry.sequence,
            message=entry.message,
            commits_range=entry.commits_range,
            test_command=entry.test_command,
            test_result=entry.test_result,
            exit_code=entry.exit_code,
            tokens_used=entry.tokens_used,
            meta=entry.meta,
            created_at=entry.created_at,
        )'''

new_ledger_response = '''class LedgerEntryResponse(BaseModel):
    id: str
    plan_id: str
    task_id: Optional[str]
    sequence: int
    message: str
    commits_range: Optional[str]
    test_command: Optional[str]
    test_result: Optional[str]
    exit_code: Optional[int]
    tokens_used: int
    meta: dict
    created_by: Optional[str] = None
    created_at: datetime

    @classmethod
    def from_orm(cls, entry: LedgerEntry) -> "LedgerEntryResponse":
        return cls(
            id=entry.id,
            plan_id=entry.plan_id,
            task_id=entry.task_id,
            sequence=entry.sequence,
            message=entry.message,
            commits_range=entry.commits_range,
            test_command=entry.test_command,
            test_result=entry.test_result,
            exit_code=entry.exit_code,
            tokens_used=entry.tokens_used,
            meta=entry.meta,
            created_by=entry.created_by,
            created_at=entry.created_at,
        )'''

content = content.replace(old_ledger_response, new_ledger_response)

with open('/var/lib/alan-portfolio/workspaces/ryan/beacon-station-ryan-vo/backend/app/api/plans.py', 'w') as f:
    f.write(content)

print('Updated response models')

