from sqlalchemy import select, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from datetime import datetime
import uuid
import os
import re

from app.models import Plan, Task, LedgerEntry, AuditLog, PlanStatus, TaskStatus, ExecutionMode
from app.core.config import settings


class PlanService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_plan(
        self,
        name: str,
        description: Optional[str] = None,
        execution_mode: ExecutionMode = ExecutionMode.SUBAGENT,
        overview_content: str = "",
        tasks: Optional[List[dict]] = None,
        user_id: Optional[str] = None,
    ) -> Plan:
        plan_id = str(uuid.uuid4())
        plan_dir = os.path.join(settings.plans_root, plan_id)
        os.makedirs(plan_dir, exist_ok=True)
        tasks_dir = os.path.join(plan_dir, "tasks")
        os.makedirs(tasks_dir, exist_ok=True)

        overview_path = os.path.join(plan_dir, "overview.md")
        with open(overview_path, "w") as f:
            f.write(overview_content or f"# {name}\n\n{description or ''}\n")

        task_files = []
        estimated_tokens = self._estimate_tokens(overview_content)
        if tasks:
            for i, task in enumerate(tasks, 1):
                task_filename = f"task-{i:03d}-{self._slugify(task['title'])}.md"
                task_path = os.path.join(tasks_dir, task_filename)
                content = f"# {task['title']}\n\n{task.get('description', '')}\n"
                with open(task_path, "w") as f:
                    f.write(content)
                task_files.append((i, task['title'], task.get('description', ''), task_path))
                estimated_tokens += self._estimate_tokens(content)

        plan = Plan(
            id=plan_id,
            name=name,
            description=description,
            execution_mode=execution_mode,
            overview_path=overview_path,
            tasks_dir=tasks_dir,
            estimated_tokens=estimated_tokens,
            created_by=user_id,
        )
        self.session.add(plan)
        await self.session.flush()

        for seq, title, desc, path in task_files:
            task = Task(
                id=str(uuid.uuid4()),
                plan_id=plan_id,
                sequence=seq,
                title=title,
                description=desc,
                file_path=path,
                estimated_tokens=self._estimate_tokens(desc or ""),
                created_by=user_id,
            )
            self.session.add(task)

        await self._audit("plan", plan_id, "create", {"name": name}, user_id)
        await self.session.commit()
        await self.session.refresh(plan)
        return plan

    async def get_plan(self, plan_id: str) -> Optional[Plan]:
        result = await self.session.execute(
            select(Plan)
            .options(selectinload(Plan.tasks), selectinload(Plan.ledger_entries))
            .where(Plan.id == plan_id)
        )
        return result.scalar_one_or_none()

    async def list_plans(
        self,
        status: Optional[PlanStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Plan], int]:
        query = select(Plan).options(selectinload(Plan.tasks))
        count_query = select(func.count(Plan.id))

        if status:
            query = query.where(Plan.status == status)
            count_query = count_query.where(Plan.status == status)

        total = (await self.session.execute(count_query)).scalar_one()
        query = query.order_by(desc(Plan.created_at)).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def update_plan(
        self,
        plan_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[PlanStatus] = None,
        overview_content: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Optional[Plan]:
        plan = await self.get_plan(plan_id)
        if not plan:
            return None

        changes = {}
        if name is not None and name != plan.name:
            changes["name"] = {"old": plan.name, "new": name}
            plan.name = name
        if description is not None and description != plan.description:
            changes["description"] = {"old": plan.description, "new": description}
            plan.description = description
        if status is not None and status != plan.status:
            changes["status"] = {"old": plan.status.value, "new": status.value}
            plan.status = status
            if status == PlanStatus.COMPLETED:
                plan.completed_at = datetime.utcnow()
        if overview_content is not None:
            with open(plan.overview_path, "w") as f:
                f.write(overview_content)
            changes["overview"] = "updated"

        if changes:
            await self._audit("plan", plan_id, "update", changes, user_id)
            await self.session.commit()
            await self.session.refresh(plan)
        return plan

    async def delete_plan(self, plan_id: str, user_id: Optional[str] = None) -> bool:
        plan = await self.get_plan(plan_id)
        if not plan:
            return False

        await self._audit("plan", plan_id, "delete", {"name": plan.name}, user_id)
        await self.session.delete(plan)
        await self.session.commit()
        return True

    async def add_task(
        self,
        plan_id: str,
        title: str,
        description: Optional[str] = None,
        sequence: Optional[int] = None,
        user_id: Optional[str] = None,
    ) -> Optional[Task]:
        plan = await self.get_plan(plan_id)
        if not plan:
            return None

        if sequence is None:
            result = await self.session.execute(
                select(func.max(Task.sequence)).where(Task.plan_id == plan_id)
            )
            sequence = (result.scalar_one() or 0) + 1

        task_filename = f"task-{sequence:03d}-{self._slugify(title)}.md"
        task_path = os.path.join(plan.tasks_dir, task_filename)
        content = f"# {title}\n\n{description or ''}\n"
        with open(task_path, "w") as f:
            f.write(content)

        task = Task(
            id=str(uuid.uuid4()),
            plan_id=plan_id,
            sequence=sequence,
            title=title,
            description=description,
            file_path=task_path,
            estimated_tokens=self._estimate_tokens(description or ""),
            created_by=user_id,
        )
        self.session.add(task)
        await self._audit("task", task.id, "create", {"title": title, "plan_id": plan_id}, user_id)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        assigned_to: Optional[str] = None,
        file_content: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Optional[Task]:
        result = await self.session.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            return None

        changes = {}
        if title is not None and title != task.title:
            changes["title"] = {"old": task.title, "new": title}
            task.title = title
        if description is not None and description != task.description:
            changes["description"] = {"old": task.description, "new": description}
            task.description = description
        if status is not None and status != task.status:
            changes["status"] = {"old": task.status.value, "new": status.value}
            task.status = status
            if status == TaskStatus.IN_PROGRESS and not task.started_at:
                task.started_at = datetime.utcnow()
            elif status == TaskStatus.COMPLETED:
                task.completed_at = datetime.utcnow()
        if assigned_to is not None:
            changes["assigned_to"] = {"old": task.assigned_to, "new": assigned_to}
            task.assigned_to = assigned_to
        if file_content is not None:
            with open(task.file_path, "w") as f:
                f.write(file_content)
            changes["file_content"] = "updated"

        if changes:
            await self._audit("task", task_id, "update", changes, user_id)
            await self.session.commit()
            await self.session.refresh(task)
        return task

    async def get_task(self, task_id: str) -> Optional[Task]:
        result = await self.session.execute(
            select(Task).options(selectinload(Task.ledger_entries)).where(Task.id == task_id)
        )
        return result.scalar_one_or_none()

    async def add_ledger_entry(
        self,
        plan_id: str,
        message: str,
        task_id: Optional[str] = None,
        commits_range: Optional[str] = None,
        test_command: Optional[str] = None,
        test_result: Optional[str] = None,
        exit_code: Optional[int] = None,
        tokens_used: int = 0,
        meta: Optional[dict] = None,
        user_id: Optional[str] = None,
    ) -> LedgerEntry:
        result = await self.session.execute(
            select(func.max(LedgerEntry.sequence)).where(LedgerEntry.plan_id == plan_id)
        )
        sequence = (result.scalar_one() or 0) + 1

        entry = LedgerEntry(
            id=str(uuid.uuid4()),
            plan_id=plan_id,
            task_id=task_id,
            sequence=sequence,
            message=message,
            commits_range=commits_range,
            test_command=test_command,
            test_result=test_result,
            exit_code=exit_code,
            tokens_used=tokens_used,
            meta=meta or {},
            created_by=user_id,
        )
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        return entry

    async def get_ledger(self, plan_id: str, limit: int = 100, offset: int = 0) -> List[LedgerEntry]:
        result = await self.session.execute(
            select(LedgerEntry)
            .where(LedgerEntry.plan_id == plan_id)
            .order_by(asc(LedgerEntry.sequence))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    def _estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        char_count = len(text)
        return max(1, char_count // 4)

    def _slugify(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s-]", "", text)
        text = re.sub(r"[\s-]+", "-", text)
        return text.strip("-")[:50]

    async def _audit(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        changes: dict,
        user_id: Optional[str],
    ) -> None:
        audit = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            changes=changes,
        )
        self.session.add(audit)