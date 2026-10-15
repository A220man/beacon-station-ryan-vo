import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.core.database import get_db, init_db, close_db, Base, engine
from app.core.config import settings
from app.models import Plan, Task, LedgerEntry, AuditLog, PlanStatus, TaskStatus


@pytest.fixture(scope="session")
async def test_engine():
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.pool import StaticPool
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    await test_engine.dispose()


@pytest.fixture
async def db_session(test_engine):
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == settings.app_version
    assert data["environment"] == settings.environment
    assert data["database"] in ["connected", "disconnected"]


@pytest.mark.asyncio
async def test_auth_test_endpoint_requires_auth(client: AsyncClient):
    response = await client.get("/api/v1/auth/test")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_plan_requires_auth(client: AsyncClient):
    response = await client.post("/api/v1/plans", json={"name": "Test Plan"})
    assert response.status_code == 401


class TestPlanService:
    @pytest.mark.asyncio
    async def test_create_plan(self, db_session: AsyncSession):
        from app.services.plan_service import PlanService
        from app.models import ExecutionMode

        service = PlanService(db_session)
        plan = await service.create_plan(
            name="Test Plan",
            description="A test plan",
            execution_mode=ExecutionMode.SUBAGENT,
            overview_content="# Test Plan\n\nOverview content",
            tasks=[
                {"title": "Task 1", "description": "First task"},
                {"title": "Task 2", "description": "Second task"},
            ],
            user_id="test-user",
        )

        assert plan.id is not None
        assert plan.name == "Test Plan"
        assert plan.description == "A test plan"
        assert plan.execution_mode == ExecutionMode.SUBAGENT
        assert plan.estimated_tokens > 0

        from sqlalchemy import select
        tasks_result = await db_session.execute(select(Task).where(Task.plan_id == plan.id))
        tasks = list(tasks_result.scalars().all())
        assert len(tasks) == 2
        assert tasks[0].title == "Task 1"
        assert tasks[1].title == "Task 2"

    @pytest.mark.asyncio
    async def test_list_plans(self, db_session: AsyncSession):
        from app.services.plan_service import PlanService
        from app.models import ExecutionMode

        service = PlanService(db_session)
        await service.create_plan("Plan 1", user_id="user1")
        await service.create_plan("Plan 2", user_id="user1")

        plans, total = await service.list_plans(limit=10, offset=0)
        assert total == 2
        assert len(plans) == 2

    @pytest.mark.asyncio
    async def test_get_plan(self, db_session: AsyncSession):
        from app.services.plan_service import PlanService
        from app.models import ExecutionMode

        service = PlanService(db_session)
        created = await service.create_plan("Test Plan", user_id="user1")
        plan = await service.get_plan(created.id)

        assert plan is not None
        assert plan.id == created.id
        assert plan.name == "Test Plan"

    @pytest.mark.asyncio
    async def test_update_plan(self, db_session: AsyncSession):
        from app.services.plan_service import PlanService
        from app.models import ExecutionMode, PlanStatus

        service = PlanService(db_session)
        created = await service.create_plan("Original", user_id="user1")
        updated = await service.update_plan(
            created.id,
            name="Updated",
            status=PlanStatus.ACTIVE,
            user_id="user1",
        )

        assert updated is not None
        assert updated.name == "Updated"
        assert updated.status == PlanStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_delete_plan(self, db_session: AsyncSession):
        from app.services.plan_service import PlanService

        service = PlanService(db_session)
        created = await service.create_plan("To Delete", user_id="user1")
        deleted = await service.delete_plan(created.id, user_id="user1")

        assert deleted is True
        plan = await service.get_plan(created.id)
        assert plan is None

    @pytest.mark.asyncio
    async def test_add_task(self, db_session: AsyncSession):
        from app.services.plan_service import PlanService

        service = PlanService(db_session)
        plan = await service.create_plan("Plan with Tasks", user_id="user1")
        task = await service.add_task(plan.id, "New Task", "Task description", user_id="user1")

        assert task is not None
        assert task.title == "New Task"
        assert task.plan_id == plan.id
        assert task.sequence == 1

    @pytest.mark.asyncio
    async def test_add_ledger_entry(self, db_session: AsyncSession):
        from app.services.plan_service import PlanService

        service = PlanService(db_session)
        plan = await service.create_plan("Plan for Ledger", user_id="user1")
        entry = await service.add_ledger_entry(
            plan_id=plan.id,
            message="Task started",
            test_command="npm test",
            test_output="Tests: 5 passed",
            exit_code=0,
            tokens_used=100,
        )

        assert entry is not None
        assert entry.message == "Task started"
        assert entry.test_command == "npm test"
        assert "5 passed" in entry.test_result or "pass" in entry.test_result

    @pytest.mark.asyncio
    async def test_get_ledger(self, db_session: AsyncSession):
        from app.services.plan_service import PlanService

        service = PlanService(db_session)
        plan = await service.create_plan("Plan for Ledger", user_id="user1")
        await service.add_ledger_entry(plan.id, "Entry 1", user_id="user1")
        await service.add_ledger_entry(plan.id, "Entry 2", user_id="user1")

        entries = await service.get_ledger(plan.id)
        assert len(entries) == 2
        assert entries[0].message == "Entry 1"
        assert entries[1].message == "Entry 2"


class TestTestParser:
    @pytest.mark.asyncio
    async def test_parse_node_test(self):
        from app.services.test_parser import parse_test_output, TestResult

        output = """# pass 5
# fail 0
# skipped 0
# duration_ms 123.45
"""
        result = parse_test_output(output, 0, "node --test")
        assert isinstance(result, TestResult)
        assert result.passed == 5
        assert result.failed == 0
        assert result.skipped == 0
        assert result.total == 5
        assert result.duration_ms == 123.45

    @pytest.mark.asyncio
    async def test_parse_pytest(self):
        from app.services.test_parser import parse_test_output

        output = """============================= test session starts ==============================
tests/test_sample.py::test_one PASSED
tests/test_sample.py::test_two PASSED
========================== 2 passed in 0.12s ===========================
"""
        result = parse_test_output(output, 0, "pytest")
        assert result.passed == 2
        assert result.failed == 0
        assert result.total == 2

    @pytest.mark.asyncio
    async def test_parse_pytest_with_failures(self):
        from app.services.test_parser import parse_test_output

        output = """============================= test session starts ==============================
tests/test_sample.py::test_one PASSED
tests/test_sample.py::test_two FAILED
========================== 1 passed, 1 failed in 0.12s ===========================
"""
        result = parse_test_output(output, 1, "pytest")
        assert result.passed == 1
        assert result.failed == 1
        assert result.total == 2

    @pytest.mark.asyncio
    async def test_parse_jest(self):
        from app.services.test_parser import parse_test_output

        output = """PASS  tests/sample.test.js
  ✓ test one (5ms)
  ✓ test two (3ms)

Test Suites: 1 passed, 1 total
Tests:       2 passed, 2 total
"""
        result = parse_test_output(output, 0, "npm test")
        assert result.passed == 2
        assert result.total == 2

    @pytest.mark.asyncio
    async def test_parse_vitest(self):
        from app.services.test_parser import parse_test_output

        output = """Test Files  1 passed (1)
Tests  3 passed (3)
"""
        result = parse_test_output(output, 0, "npm test")
        assert result.passed == 3
        assert result.total == 3

    @pytest.mark.asyncio
    async def test_parse_cargo_test(self):
        from app.services.test_parser import parse_test_output

        output = """test result: ok. 10 passed; 0 failed; 2 ignored; 0 measured; 0 filtered out"""
        result = parse_test_output(output, 0, "cargo test")
        assert result.passed == 10
        assert result.failed == 0
        assert result.skipped == 2
        assert result.total == 12

    @pytest.mark.asyncio
    async def test_parse_go_test(self):
        from app.services.test_parser import parse_test_output

        output = """=== RUN   TestOne
--- PASS: TestOne (0.00s)
=== RUN   TestTwo
--- PASS: TestTwo (0.00s)
ok      example.com/pkg  0.012s"""
        result = parse_test_output(output, 0, "go test")
        assert result.passed == 2
        assert result.total == 2
        assert result.duration_ms is not None

    @pytest.mark.asyncio
    async def test_ledger_string_format(self):
        from app.services.test_parser import TestResult

        result = TestResult(passed=5, failed=0, skipped=0, total=5, duration_ms=100.0)
        assert result.to_ledger_string() == "5/5 pass; 100.0ms"

        result = TestResult(passed=3, failed=1, skipped=2, total=6)
        assert result.to_ledger_string() == "3/6 pass; 1 fail; 2 skipped"