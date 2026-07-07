from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.domain.entities.appointment import Appointment
from src.domain.entities.client import Client
from src.domain.entities.employee import Employee
from src.domain.entities.organization import Organization
from src.domain.entities.organization_member import OrganizationMember, OrganizationRole
from src.domain.entities.service import Service
from src.domain.entities.user import User
from src.infrastructure.database.base import Base
from src.infrastructure.database.repositories.appointment import SQLAlchemyAppointmentRepository
from src.infrastructure.database.repositories.client import SQLAlchemyClientRepository
from src.infrastructure.database.repositories.employee import SQLAlchemyEmployeeRepository
from src.infrastructure.database.repositories.organization import SQLAlchemyOrganizationRepository
from src.infrastructure.database.repositories.organization_member import (
    SQLAlchemyOrganizationMemberRepository,
)
from src.infrastructure.database.repositories.service import SQLAlchemyServiceRepository
from src.infrastructure.database.repositories.user import SQLAlchemyUserRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork

TEST_DATABASE_URL = "postgresql+asyncpg://bookflow:bookflow@localhost:5432/bookflow"


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncGenerator[AsyncSession]:
    async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_factory() as s:
        try:
            yield s
        finally:
            await s.rollback()


@pytest_asyncio.fixture
def uow(session: AsyncSession) -> SQLAlchemyUnitOfWork:
    return SQLAlchemyUnitOfWork(session)


# ── Repository fixtures ──


@pytest_asyncio.fixture
def user_repo(session: AsyncSession) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(session)


@pytest_asyncio.fixture
def org_repo(session: AsyncSession) -> SQLAlchemyOrganizationRepository:
    return SQLAlchemyOrganizationRepository(session)


@pytest_asyncio.fixture
def org_member_repo(session: AsyncSession) -> SQLAlchemyOrganizationMemberRepository:
    return SQLAlchemyOrganizationMemberRepository(session)


@pytest_asyncio.fixture
def employee_repo(session: AsyncSession) -> SQLAlchemyEmployeeRepository:
    return SQLAlchemyEmployeeRepository(session)


@pytest_asyncio.fixture
def service_repo(session: AsyncSession) -> SQLAlchemyServiceRepository:
    return SQLAlchemyServiceRepository(session)


@pytest_asyncio.fixture
def client_repo(session: AsyncSession) -> SQLAlchemyClientRepository:
    return SQLAlchemyClientRepository(session)


@pytest_asyncio.fixture
def appointment_repo(session: AsyncSession) -> SQLAlchemyAppointmentRepository:
    return SQLAlchemyAppointmentRepository(session)


# ── Seed entity fixtures ──


@pytest_asyncio.fixture
async def seed_user(user_repo: SQLAlchemyUserRepository) -> User:
    user = User(email="test@example.com", hashed_password="hash123")
    return await user_repo.add(user)


@pytest_asyncio.fixture
async def seed_org(org_repo: SQLAlchemyOrganizationRepository) -> Organization:
    org = Organization(name="Test Org", slug="test-org")
    return await org_repo.add(org)


@pytest_asyncio.fixture
async def seed_org_member(
    org_member_repo: SQLAlchemyOrganizationMemberRepository,
    seed_user: User,
    seed_org: Organization,
) -> OrganizationMember:
    member = OrganizationMember(
        user_id=seed_user.id,
        organization_id=seed_org.id,
        role=OrganizationRole.ADMIN,
    )
    return await org_member_repo.add(member)


@pytest_asyncio.fixture
async def seed_employee(
    employee_repo: SQLAlchemyEmployeeRepository,
    seed_org: Organization,
) -> Employee:
    emp = Employee(
        organization_id=seed_org.id,
        name="Alice",
        email="alice@test.com",
    )
    return await employee_repo.add(emp)


@pytest_asyncio.fixture
async def seed_service(
    service_repo: SQLAlchemyServiceRepository,
    seed_org: Organization,
) -> Service:
    svc = Service(
        organization_id=seed_org.id,
        name="Consulting",
        price=Decimal("150.00"),
        duration_minutes=60,
    )
    return await service_repo.add(svc)


@pytest_asyncio.fixture
async def seed_client(
    client_repo: SQLAlchemyClientRepository,
    seed_org: Organization,
) -> Client:
    cl = Client(
        organization_id=seed_org.id,
        name="Bob",
        email="bob@test.com",
    )
    return await client_repo.add(cl)


@pytest_asyncio.fixture
async def seed_appointment(
    appointment_repo: SQLAlchemyAppointmentRepository,
    seed_org: Organization,
    seed_employee: Employee,
    seed_client: Client,
    seed_service: Service,
) -> Appointment:
    now = datetime.now(UTC)
    apt = Appointment(
        organization_id=seed_org.id,
        employee_id=seed_employee.id,
        client_id=seed_client.id,
        service_id=seed_service.id,
        starts_at=now + timedelta(days=1),
        ends_at=now + timedelta(days=1, hours=1),
    )
    return await appointment_repo.add(apt)
