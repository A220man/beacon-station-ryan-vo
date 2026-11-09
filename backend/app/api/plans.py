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

class TokenEstimateResponse(BaseModel):
    plan_id: str
    estimated_tokens: int
    overview_tokens: int
    task_tokens: int
    ledger_tokens: int
    breakdown: dict


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
    execution_mode: Optional[ExecutionMode] = None
    overview_content: Optional[str] = None


class TaskResponse(BaseModel):
    id: str
    plan_id: str
    sequence: int
    title: str
    description: Optional[str]
    status: TaskStatus
    file_path: Optional[str]
    file_content: Optional[str]
    estimated_tokens: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, task: Task) -> "TaskResponse":
        return cls(
            id=task.id,
            plan_id=task.plan_id,
            sequence=task.sequence,
            title=task.title,
            description=task.description,
            status=task.status,
            file_path=task.file_path,
            file_content=task.file_content,
            estimated_tokens=task.estimated_tokens,
            started_at=task.started_at,
            completed_at=task.completed_at,
            created_by=task.created_by,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )



class LedgerEntryResponse(BaseModel):
    id: str
    plan_id: str
    message: str
    entry_type: str
    tokens_used: Optional[int]
    test_result: Optional[str]
    exit_code: Optional[int]
    commit_hash: Optional[str]
    meta: Optional[dict]
    created_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, entry: LedgerEntry) -> "LedgerEntryResponse":
        return cls(
            id=entry.id,
            plan_id=entry.plan_id,
            message=entry.message,
            entry_type=entry.entry_type,
            tokens_used=entry.tokens_used,
            test_result=entry.test_result,
            exit_code=entry.exit_code,
            commit_hash=entry.commit_hash,
            meta=entry.meta,
            created_at=entry.created_at,
            created_by=entry.created_by,
        )



class PlanResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    execution_mode: ExecutionMode
    status: PlanStatus
    overview_path: str
    tasks_dir: str
    estimated_tokens: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    tasks: List[TaskResponse] = []
    ledger_entries: List[LedgerEntryResponse] = []

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, plan: Plan) -> "PlanResponse":
        return cls(
            id=plan.id,
            name=plan.name,
            description=plan.description,
            execution_mode=plan.execution_mode,
            status=plan.status,
            overview_path=plan.overview_path,
            tasks_dir=plan.tasks_dir,
            estimated_tokens=plan.estimated_tokens,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
            created_by=plan.created_by,
            tasks=[
                TaskResponse.from_orm(t) for t in sorted(plan.tasks, key=lambda x: x.sequence)
            ] if plan.tasks else [],
            ledger_entries=[
                LedgerEntryResponse.from_orm(e) for e in plan.ledger_entries
            ] if plan.ledger_entries else [],
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
    user: TokenClaims = Depends(get_current_user),
):
    service = PlanService(db)
    plan = await service.create_plan(
        name=data.name,
        description=data.description,
        execution_mode=data.execution_mode,
        overview_content=data.overview_content,
        tasks=data.tasks,
        user_id=user.sub,
    )
    return PlanResponse.from_orm(plan)


@router.get("", response_model=PlanListResponse)
async def list_plans(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[PlanStatus] = None,
    db: AsyncSession = Depends(get_db),
    user: TokenClaims = Depends(get_current_user),
):
    service = PlanService(db)
    plans, total = await service.list_plans(limit=limit, offset=offset, status=status)
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
    user: TokenClaims = Depends(get_current_user),
):
    service = PlanService(db)
    plan = await service.update_plan(
        plan_id=plan_id,
        name=data.name,
        description=data.description,
        status=data.status,
        execution_mode=data.execution_mode,
        overview_content=data.overview_content,
        user_id=user.sub,
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return PlanResponse.from_orm(plan)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    user: TokenClaims = Depends(get_current_user),
):
    service = PlanService(db)
    deleted = await service.delete_plan(plan_id, user_id=user.sub)
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
    file_content: Optional[str] = None



@router.post("/{plan_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def add_task(
    plan_id: str,
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    user: TokenClaims = Depends(get_current_user),
):
    service = PlanService(db)
    task = await service.add_task(
        plan_id=plan_id,
        title=data.title,
        description=data.description,
        sequence=data.sequence,
        user_id=user.sub,
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
    user: TokenClaims = Depends(get_current_user),
):
    service = PlanService(db)
    task = await service.update_task(
        task_id=task_id,
        title=data.title,
        description=data.description,
        status=data.status,
        file_content=data.file_content,
        user_id=user.sub,
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.from_orm(task)


class LedgerEntryCreate(BaseModel):
    message: str
    entry_type: str = "info"
    tokens_used: Optional[int] = None
    test_result: Optional[str] = None
    exit_code: Optional[int] = None
    commit_hash: Optional[str] = None
    meta: Optional[dict] = None



@router.post("/{plan_id}/ledger", response_model=LedgerEntryResponse, status_code=status.HTTP_201_CREATED)
async def add_ledger_entry(
    plan_id: str,
    data: LedgerEntryCreate,
    db: AsyncSession = Depends(get_db),
    user: TokenClaims = Depends(get_current_user),
):
    service = PlanService(db)
    plan = await service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    entry = await service.add_ledger_entry(
        plan_id=plan_id,
        message=data.message,
        entry_type=data.entry_type,
        tokens_used=data.tokens_used,
        test_result=data.test_result,
        exit_code=data.exit_code,
        commit_hash=data.commit_hash,
        meta=data.meta,
        user_id=user.sub,
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


@router.get("/{plan_id}/estimate-tokens", response_model=TokenEstimateResponse)
async def estimate_tokens(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    user: TokenClaims = Depends(get_current_user),
):
    service = PlanService(db)
    plan = await service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    overview_tokens = service._estimate_tokens(plan.description or "")
    task_tokens = sum(service._estimate_tokens(t.description or "") + service._estimate_tokens(t.title) for t in plan.tasks)
    ledger_tokens = sum(service._estimate_tokens(e.message) for e in plan.ledger_entries)
    total = overview_tokens + task_tokens + ledger_tokens

    return TokenEstimateResponse(
        plan_id=plan.id,
        estimated_tokens=total,
        overview_tokens=overview_tokens,
        task_tokens=task_tokens,
        ledger_tokens=ledger_tokens,
        breakdown={
            "overview_chars": len(plan.description or ""),
            "task_chars": sum(len(t.description or "") + len(t.title) for t in plan.tasks),
            "ledger_chars": sum(len(e.message) for e in plan.ledger_entries),
            "task_count": len(plan.tasks),
            "ledger_entry_count": len(plan.ledger_entries),
        },
    )
