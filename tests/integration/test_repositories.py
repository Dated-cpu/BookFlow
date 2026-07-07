import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from src.domain.entities.appointment import Appointment, AppointmentStatus
from src.domain.entities.client import Client
from src.domain.entities.employee import Employee
from src.domain.entities.organization import Organization
from src.domain.entities.organization_member import OrganizationMember, OrganizationRole
from src.domain.entities.service import Service
from src.domain.entities.user import User

# ── UserRepository ──


class TestUserRepository:
    async def test_add_and_get_by_id(self, user_repo):
        user = User(email="alice@example.com", hashed_password="hash")
        saved = await user_repo.add(user)
        assert saved.id is not None
        assert saved.email == "alice@example.com"

        fetched = await user_repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.email == "alice@example.com"

    async def test_get_by_email(self, user_repo):
        user = User(email="bob@example.com", hashed_password="hash")
        await user_repo.add(user)

        fetched = await user_repo.get_by_email("bob@example.com")
        assert fetched is not None
        assert fetched.email == "bob@example.com"

        not_found = await user_repo.get_by_email("nonexistent@example.com")
        assert not_found is None

    async def test_update(self, user_repo):
        user = User(email="carol@example.com", hashed_password="hash")
        saved = await user_repo.add(user)

        saved.change_email("carol@new.com")
        updated = await user_repo.update(saved)
        assert updated.email == "carol@new.com"

        fetched = await user_repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.email == "carol@new.com"

    async def test_delete(self, user_repo):
        user = User(email="dave@example.com", hashed_password="hash")
        saved = await user_repo.add(user)

        await user_repo.delete(saved)
        fetched = await user_repo.get_by_id(saved.id)
        assert fetched is None

    async def test_list(self, user_repo):
        await user_repo.add(User(email="eve@example.com", hashed_password="hash"))
        await user_repo.add(User(email="frank@example.com", hashed_password="hash"))

        users = await user_repo.list()
        assert len(users) >= 2

    async def test_update_nonexistent_raises(self, user_repo):
        fake_user = User(email="ghost@example.com", hashed_password="hash")
        fake_user.id = uuid.uuid4()
        with pytest.raises(ValueError, match="not found"):
            await user_repo.update(fake_user)


# ── OrganizationRepository ──


class TestOrganizationRepository:
    async def test_add_and_get_by_slug(self, org_repo):
        org = Organization(name="Acme Corp", slug="acme")
        saved = await org_repo.add(org)
        assert saved.slug == "acme"

        fetched = await org_repo.get_by_slug("acme")
        assert fetched is not None
        assert fetched.name == "Acme Corp"

    async def test_rename(self, org_repo):
        org = Organization(name="Old Name", slug="old-name")
        saved = await org_repo.add(org)

        saved.rename("New Name")
        updated = await org_repo.update(saved)
        assert updated.name == "New Name"

    async def test_list(self, org_repo):
        await org_repo.add(Organization(name="Org A", slug="org-a"))
        await org_repo.add(Organization(name="Org B", slug="org-b"))

        orgs = await org_repo.list()
        assert len(orgs) >= 2


# ── OrganizationMemberRepository ──


class TestOrganizationMemberRepository:
    async def test_add(self, org_member_repo, seed_user, seed_org):
        member = OrganizationMember(
            user_id=seed_user.id,
            organization_id=seed_org.id,
            role=OrganizationRole.OWNER,
        )
        saved = await org_member_repo.add(member)
        assert saved.role == OrganizationRole.OWNER

        fetched = await org_member_repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.user_id == seed_user.id

    async def test_change_role(self, org_member_repo, seed_user, seed_org):
        member = OrganizationMember(
            user_id=seed_user.id,
            organization_id=seed_org.id,
            role=OrganizationRole.EMPLOYEE,
        )
        saved = await org_member_repo.add(member)

        saved.change_role(OrganizationRole.ADMIN)
        updated = await org_member_repo.update(saved)
        assert updated.role == OrganizationRole.ADMIN


# ── EmployeeRepository ──


class TestEmployeeRepository:
    async def test_add_and_get(self, employee_repo, seed_org):
        emp = Employee(
            organization_id=seed_org.id,
            name="Alice",
            email="alice@example.com",
        )
        saved = await employee_repo.add(emp)
        assert saved.name == "Alice"

        fetched = await employee_repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.email == "alice@example.com"

    async def test_activate_deactivate(self, employee_repo, seed_org):
        emp = Employee(
            organization_id=seed_org.id,
            name="Bob",
            email="bob@example.com",
        )
        saved = await employee_repo.add(emp)
        assert saved.is_active is True

        saved.deactivate()
        updated = await employee_repo.update(saved)
        assert updated.is_active is False

        updated.activate()
        updated = await employee_repo.update(updated)
        assert updated.is_active is True

    async def test_list(self, employee_repo, seed_org):
        await employee_repo.add(
            Employee(
                organization_id=seed_org.id,
                name="A",
                email="a@test.com",
            )
        )
        await employee_repo.add(
            Employee(
                organization_id=seed_org.id,
                name="B",
                email="b@test.com",
            )
        )
        employees = await employee_repo.list()
        assert len(employees) >= 2


# ── ServiceRepository ──


class TestServiceRepository:
    async def test_add_and_change_price(self, service_repo, seed_org):
        svc = Service(
            organization_id=seed_org.id,
            name="Consulting",
            price=Decimal("100.00"),
            duration_minutes=60,
        )
        saved = await service_repo.add(svc)
        assert saved.price == Decimal("100.00")

        saved.change_price(Decimal("150.00"))
        updated = await service_repo.update(saved)
        assert updated.price == Decimal("150.00")

    async def test_get_by_id_not_found(self, service_repo):
        fetched = await service_repo.get_by_id(uuid.uuid4())
        assert fetched is None


# ── ClientRepository ──


class TestClientRepository:
    async def test_add_and_change_phone(self, client_repo, seed_org):
        cl = Client(
            organization_id=seed_org.id,
            name="Carol",
            email="carol@example.com",
        )
        saved = await client_repo.add(cl)
        assert saved.phone is None

        saved.change_phone("+1234567890")
        updated = await client_repo.update(saved)
        assert updated.phone == "+1234567890"

    async def test_list(self, client_repo, seed_org):
        await client_repo.add(
            Client(
                organization_id=seed_org.id,
                name="A",
                email="a@test.com",
            )
        )
        clients = await client_repo.list()
        assert len(clients) >= 1


# ── AppointmentRepository ──


class TestAppointmentRepository:
    async def test_add_and_get(
        self, appointment_repo, seed_org, seed_employee, seed_client, seed_service
    ):
        now = datetime.now(UTC)
        apt = Appointment(
            organization_id=seed_org.id,
            employee_id=seed_employee.id,
            client_id=seed_client.id,
            service_id=seed_service.id,
            starts_at=now + timedelta(days=2),
            ends_at=now + timedelta(days=2, hours=1),
        )
        saved = await appointment_repo.add(apt)
        assert saved.status == AppointmentStatus.SCHEDULED

        fetched = await appointment_repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.starts_at <= fetched.ends_at

    async def test_cancel(self, appointment_repo, seed_appointment):
        seed_appointment.cancel()
        updated = await appointment_repo.update(seed_appointment)
        assert updated.status == AppointmentStatus.CANCELLED

    async def test_reschedule(self, appointment_repo, seed_appointment):
        now = datetime.now(UTC)
        new_start = now + timedelta(days=5)
        new_end = now + timedelta(days=5, hours=2)
        seed_appointment.reschedule(new_start, new_end)
        updated = await appointment_repo.update(seed_appointment)
        assert updated.starts_at == new_start
        assert updated.ends_at == new_end

    async def test_list_for_employee(
        self, appointment_repo, seed_org, seed_employee, seed_client, seed_service
    ):
        now = datetime.now(UTC)
        for i in range(3):
            apt = Appointment(
                organization_id=seed_org.id,
                employee_id=seed_employee.id,
                client_id=seed_client.id,
                service_id=seed_service.id,
                starts_at=now + timedelta(days=10 + i),
                ends_at=now + timedelta(days=10 + i, hours=1),
            )
            await appointment_repo.add(apt)

        appointments = await appointment_repo.list_for_employee(seed_employee.id)
        assert len(appointments) >= 3

    async def test_list_for_client(
        self, appointment_repo, seed_org, seed_employee, seed_client, seed_service
    ):
        now = datetime.now(UTC)
        apt = Appointment(
            organization_id=seed_org.id,
            employee_id=seed_employee.id,
            client_id=seed_client.id,
            service_id=seed_service.id,
            starts_at=now + timedelta(days=15),
            ends_at=now + timedelta(days=15, hours=1),
        )
        await appointment_repo.add(apt)

        appointments = await appointment_repo.list_for_client(seed_client.id)
        assert len(appointments) >= 1

    async def test_list_between_dates(
        self, appointment_repo, seed_org, seed_employee, seed_client, seed_service
    ):
        now = datetime.now(UTC)
        apt = Appointment(
            organization_id=seed_org.id,
            employee_id=seed_employee.id,
            client_id=seed_client.id,
            service_id=seed_service.id,
            starts_at=now + timedelta(days=20),
            ends_at=now + timedelta(days=20, hours=1),
        )
        saved = await appointment_repo.add(apt)

        # Appointments starting between day 19 and day 21
        results = await appointment_repo.list_between_dates(
            now + timedelta(days=19),
            now + timedelta(days=21),
        )
        assert any(a.id == saved.id for a in results)

    async def test_delete(self, appointment_repo, seed_appointment):
        await appointment_repo.delete(seed_appointment)
        fetched = await appointment_repo.get_by_id(seed_appointment.id)
        assert fetched is None
