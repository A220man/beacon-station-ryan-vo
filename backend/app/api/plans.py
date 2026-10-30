from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user, require_role, TokenClaims
from app.services.plan_service import PlanService
from app.services.test_parser import parse_test_output
from app.models import Plan, Task, LedgerEntry, PlanStatus, TaskStatus, ExecutionMode

router = APIRouter(prefix="/plans", tags=["plans"])


class PlanCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    execution_mode: ExecutionMode = ExecutionMode.SUBAGENT
    overview_content: str = ""
    tasks: Optional[List[dict]] = None


class PlanUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[PlanStatus] = None
    overview_content: Optional[str] = None


class PlanResponse(BaseModel):
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
        )


class PlanListResponse(BaseModel):
    plans: List[PlanResponse]
    total: int
    limit: int
    offset: int


@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    data: PlanCreate,
    db: AsyncSession = Depends(get_db),
    user: TokenClaims = Depends(require_role("operator", "admin")),
):
    service = PlanService(db)
    plan = await service.create_plan(
        name=data.name,
        description=data.description,
        execution_mode=data.execution_mode,
        overview_content=data.overview_content,
        tasks=data.tasks,
        user_id=user.id,
    )
    return PlanResponse.from_orm(plan)


@router.get("", response_model=PlanListResponse)
async def list_plans(
    status_filter: Optional[PlanStatus] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: TokenClaims = Depends(get_current_user),
):
    service = PlanService(db)
    plans, total = await service.list_plans(status=status_filter, limit=limit, offset=offset)
    return PlanListResponse(
        plans=[PlanResponse.from_orm(p) for p in plans],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    user: TokenClaims = Depends(get_current_user),
):
    service = PlanService(db)
    plan = await service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return PlanResponse.from_orm(plan)


@router.patch("/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: str,
    data: PlanUpdate,
    db: AsyncSession = Depends(get_db),
    user: TokenClaims = Depends(require_role("operator", "admin")),
):
    service = PlanService(db)
    plan = await service.update_plan(
        plan_id=plan_id,
        name=data.name,
        description=data.description,
        status=data.status,
        overview_content=data.overview_content,
        user_id=user.id,
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return PlanResponse.from_orm(plan)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    user: TokenClaims = Depends(require_role("admin")),
):
    service = PlanService(db)
    deleted = await service.delete_plan(plan_id, user_id=user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Plan not found")


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    sequence: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    assigned_to: Optional[str] = None
    file_content: Optional[str] = None


class TaskResponse(BaseModel):
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
        )


@router.post("/{plan_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def add_task(
    plan_id: str,
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    user: TokenClaims = Depends(require_role("operator", "admin")),
):
    service = PlanService(db)
    task = await service.add_task(
        plan_id=plan_id,
        title=data.title,
        description=data.description,
        sequence=data.sequence,
        user_id=user.id,
    )
    if not task:
        raise HTTPException(status_code=404, detail="Plan not found")
    return TaskResponse.from_orm(task)


@router.get("/{plan_id}/tasks", response_model=List[TaskResponse])
async def list_tasks(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    user: TokenClaims = Depends(get_current_user),
):
    service = PlanService(db)
    plan = await service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return [TaskResponse.from_orm(t) for t in sorted(plan.tasks, key=lambda x: x.sequence)]


@router.get("/{plan_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    plan_id: str,
    task_id: str,
    db: AsyncSession = Depends(get_db),
    user: TokenClaims = Depends(get_current_user),
):
    service = PlanService(db)
    task = await service.get_task(task_id)
    if not task or task.plan_id != plan_id:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.from_orm(task)


@router.patch("/{plan_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    plan_id: str,
    task_id: str,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    user: TokenClaims = Depends(require_role("operator", "admin")),
):
    service = PlanService(db)
    task = await service.update_task(
        task_id=task_id,
        title=data.title,
        description=data.description,
        status=data.status,
        assigned_to=data.assigned_to,
        file_content=data.file_content,
        user_id=user.id,
    )
    if not task or task.plan_id != plan_id:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.from_orm(task)


class LedgerEntryCreate(BaseModel):
    message: str
    task_id: Optional[str] = None
    commits_range: Optional[str] = None
    test_command: Optional[str] = None
    test_output: Optional[str] = None
    exit_code: Optional[int] = None
    tokens_used: int = 0
    meta: Optional[dict] = None


class LedgerEntryResponse(BaseModel):
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
        )


@router.post("/{plan_id}/ledger", response_model=LedgerEntryResponse, status_code=status.HTTP_201_CREATED)
async def add_ledger_entry(
    plan_id: str,
    data: LedgerEntryCreate,
    db: AsyncSession = Depends(get_db),
    user: TokenClaims = Depends(require_role("operator", "admin")),
):
    service = PlanService(db)
    plan = await service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    test_result = None
    if data.test_command and data.test_output is not None:
        parsed = parse_test_output(data.test_output, data.exit_code or 0, data.test_command)
        test_result = parsed.to_ledger_string()

    entry = await service.add_ledger_entry(
        plan_id=plan_id,
        message=data.message,
        task_id=data.task_id,
        commits_range=data.commits_range,
        test_command=data.test_command,
        test_result=test_result,
        exit_code=data.exit_code,
        tokens_used=data.tokens_used,
        meta=data.meta,
        user_id=user.id,
    )
    return LedgerEntryResponse.from_orm(entry)


@router.get("/{plan_id}/ledger", response_model=List[LedgerEntryResponse])
async def get_ledger(
    plan_id: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: TokenClaims = Depends(get_current_user),
):
    service = PlanService(db)
    plan = await service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    entries = await service.get_ledger(plan_id, limit=limit, offset=offset)
    return [LedgerEntryResponse.from_orm(e) for e in entries]