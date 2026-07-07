import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from src.infrastructure.database.models.client import ClientModel

TEST_DATABASE_URL = "postgresql+asyncpg://bookflow:bookflow@localhost:5432/bookflow"


class TestAppointmentsAPI:
    async def _register_and_login(self, client, email: str, password: str = "Pass1234"):
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password},
        )
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        return resp.json()["access_token"]

    async def _create_org(self, client, token: str, name: str):
        resp = await client.post(
            "/api/v1/organizations",
            json={"name": name},
            headers={"Authorization": f"Bearer {token}"},
        )
        return resp.json()["id"]

    async def _create_client_direct(self, org_id: str, email: str) -> str:
        engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
        async with engine.begin() as conn:
            client_id = uuid.uuid4()
            stmt = insert(ClientModel).values(
                id=client_id,
                organization_id=uuid.UUID(org_id),
                name="Test Client",
                email=email,
            )
            await conn.execute(stmt)
        await engine.dispose()
        return str(client_id)

    async def test_create_appointment(self, client):
        token = await self._register_and_login(client, "apt_create@test.com")
        org_id = await self._create_org(client, token, "AptCreateOrg")

        emp_resp = await client.post(
            "/api/v1/employees",
            json={"organization_id": org_id, "name": "Emp", "email": "emp@test.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        emp_id = emp_resp.json()["id"]

        svc_resp = await client.post(
            "/api/v1/services",
            json={
                "organization_id": org_id,
                "name": "Consulting",
                "price": "150.00",
                "duration_minutes": 60,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        svc_id = svc_resp.json()["id"]

        client_id = await self._create_client_direct(org_id, "cli@test.com")

        now = datetime.now(UTC)
        response = await client.post(
            "/api/v1/appointments",
            json={
                "organization_id": org_id,
                "employee_id": emp_id,
                "client_id": client_id,
                "service_id": svc_id,
                "starts_at": (now + timedelta(hours=2)).isoformat(),
                "ends_at": (now + timedelta(hours=3)).isoformat(),
                "notes": "Test appointment",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "scheduled"
        assert data["notes"] == "Test appointment"
        assert data["organization_id"] == org_id
        assert data["employee_id"] == emp_id

    async def test_create_appointment_overlap(self, client):
        token = await self._register_and_login(client, "apt_overlap@test.com")
        org_id = await self._create_org(client, token, "AptOverlapOrg")

        emp_resp = await client.post(
            "/api/v1/employees",
            json={"organization_id": org_id, "name": "EmpO", "email": "empo@test.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        emp_id = emp_resp.json()["id"]

        svc_resp = await client.post(
            "/api/v1/services",
            json={
                "organization_id": org_id,
                "name": "Massage",
                "price": "80.00",
                "duration_minutes": 60,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        svc_id = svc_resp.json()["id"]

        client_id = await self._create_client_direct(org_id, "clio@test.com")

        now = datetime.now(UTC)
        # First appointment
        resp1 = await client.post(
            "/api/v1/appointments",
            json={
                "organization_id": org_id,
                "employee_id": emp_id,
                "client_id": client_id,
                "service_id": svc_id,
                "starts_at": (now + timedelta(hours=2)).isoformat(),
                "ends_at": (now + timedelta(hours=3)).isoformat(),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp1.status_code == 201

        # Overlapping appointment should fail
        resp2 = await client.post(
            "/api/v1/appointments",
            json={
                "organization_id": org_id,
                "employee_id": emp_id,
                "client_id": client_id,
                "service_id": svc_id,
                "starts_at": (now + timedelta(hours=2, minutes=30)).isoformat(),
                "ends_at": (now + timedelta(hours=3, minutes=30)).isoformat(),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp2.status_code == 400
        assert "time slot" in resp2.json()["detail"]

    async def test_list_appointments(self, client):
        token = await self._register_and_login(client, "apt_list@test.com")
        org_id = await self._create_org(client, token, "AptListOrg")

        emp_resp = await client.post(
            "/api/v1/employees",
            json={"organization_id": org_id, "name": "EmpL", "email": "empl@test.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        emp_id = emp_resp.json()["id"]

        svc_resp = await client.post(
            "/api/v1/services",
            json={
                "organization_id": org_id,
                "name": "ServiceL",
                "price": "50.00",
                "duration_minutes": 30,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        svc_id = svc_resp.json()["id"]

        client_id = await self._create_client_direct(org_id, "clil@test.com")

        now = datetime.now(UTC)
        for i in range(2):
            await client.post(
                "/api/v1/appointments",
                json={
                    "organization_id": org_id,
                    "employee_id": emp_id,
                    "client_id": client_id,
                    "service_id": svc_id,
                    "starts_at": (now + timedelta(days=1 + i, hours=2)).isoformat(),
                    "ends_at": (now + timedelta(days=1 + i, hours=3)).isoformat(),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        response = await client.get(
            f"/api/v1/appointments?organization_id={org_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_get_appointment_by_id(self, client):
        token = await self._register_and_login(client, "apt_get@test.com")
        org_id = await self._create_org(client, token, "AptGetOrg")

        emp_resp = await client.post(
            "/api/v1/employees",
            json={"organization_id": org_id, "name": "EmpG", "email": "empg@test.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        emp_id = emp_resp.json()["id"]

        svc_resp = await client.post(
            "/api/v1/services",
            json={
                "organization_id": org_id,
                "name": "ServiceG",
                "price": "30.00",
                "duration_minutes": 30,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        svc_id = svc_resp.json()["id"]

        client_id = await self._create_client_direct(org_id, "clig@test.com")

        now = datetime.now(UTC)
        create_resp = await client.post(
            "/api/v1/appointments",
            json={
                "organization_id": org_id,
                "employee_id": emp_id,
                "client_id": client_id,
                "service_id": svc_id,
                "starts_at": (now + timedelta(hours=2)).isoformat(),
                "ends_at": (now + timedelta(hours=3)).isoformat(),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        apt_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/appointments/{apt_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == apt_id
        assert data["status"] == "scheduled"

    async def test_update_appointment_reschedule(self, client):
        token = await self._register_and_login(client, "apt_upd@test.com")
        org_id = await self._create_org(client, token, "AptUpdOrg")

        emp_resp = await client.post(
            "/api/v1/employees",
            json={"organization_id": org_id, "name": "EmpU", "email": "empu@test.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        emp_id = emp_resp.json()["id"]

        svc_resp = await client.post(
            "/api/v1/services",
            json={
                "organization_id": org_id,
                "name": "ServiceU",
                "price": "40.00",
                "duration_minutes": 30,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        svc_id = svc_resp.json()["id"]

        client_id = await self._create_client_direct(org_id, "cliu@test.com")

        now = datetime.now(UTC)
        create_resp = await client.post(
            "/api/v1/appointments",
            json={
                "organization_id": org_id,
                "employee_id": emp_id,
                "client_id": client_id,
                "service_id": svc_id,
                "starts_at": (now + timedelta(hours=2)).isoformat(),
                "ends_at": (now + timedelta(hours=3)).isoformat(),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        apt_id = create_resp.json()["id"]

        new_start = (now + timedelta(hours=5)).isoformat()
        new_end = (now + timedelta(hours=6)).isoformat()
        response = await client.put(
            f"/api/v1/appointments/{apt_id}",
            json={
                "starts_at": new_start,
                "ends_at": new_end,
                "notes": "Rescheduled",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == "Rescheduled"
        assert data["status"] == "scheduled"

    async def test_cancel_appointment(self, client):
        token = await self._register_and_login(client, "apt_cancel@test.com")
        org_id = await self._create_org(client, token, "AptCancelOrg")

        emp_resp = await client.post(
            "/api/v1/employees",
            json={"organization_id": org_id, "name": "EmpC", "email": "empc@test.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        emp_id = emp_resp.json()["id"]

        svc_resp = await client.post(
            "/api/v1/services",
            json={
                "organization_id": org_id,
                "name": "ServiceC",
                "price": "20.00",
                "duration_minutes": 30,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        svc_id = svc_resp.json()["id"]

        client_id = await self._create_client_direct(org_id, "clic@test.com")

        now = datetime.now(UTC)
        create_resp = await client.post(
            "/api/v1/appointments",
            json={
                "organization_id": org_id,
                "employee_id": emp_id,
                "client_id": client_id,
                "service_id": svc_id,
                "starts_at": (now + timedelta(hours=2)).isoformat(),
                "ends_at": (now + timedelta(hours=3)).isoformat(),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        apt_id = create_resp.json()["id"]

        delete_resp = await client.delete(
            f"/api/v1/appointments/{apt_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert delete_resp.status_code == 204

        get_resp = await client.get(
            f"/api/v1/appointments/{apt_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["status"] == "cancelled"

    async def test_appointment_from_other_org(self, client):
        token_a = await self._register_and_login(client, "apt_orga@test.com")
        token_b = await self._register_and_login(client, "apt_orgb@test.com")

        org_a = await self._create_org(client, token_a, "AptOrgA")
        await self._create_org(client, token_b, "AptOrgB")

        emp_resp = await client.post(
            "/api/v1/employees",
            json={"organization_id": org_a, "name": "EmpAO", "email": "empao@test.com"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        emp_id = emp_resp.json()["id"]

        svc_resp = await client.post(
            "/api/v1/services",
            json={
                "organization_id": org_a,
                "name": "ServiceAO",
                "price": "10.00",
                "duration_minutes": 15,
            },
            headers={"Authorization": f"Bearer {token_a}"},
        )
        svc_id = svc_resp.json()["id"]

        client_id = await self._create_client_direct(org_a, "cliao@test.com")

        now = datetime.now(UTC)
        create_resp = await client.post(
            "/api/v1/appointments",
            json={
                "organization_id": org_a,
                "employee_id": emp_id,
                "client_id": client_id,
                "service_id": svc_id,
                "starts_at": (now + timedelta(hours=2)).isoformat(),
                "ends_at": (now + timedelta(hours=3)).isoformat(),
            },
            headers={"Authorization": f"Bearer {token_a}"},
        )
        apt_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/appointments/{apt_id}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]

    async def test_create_appointment_inactive_employee(self, client):
        token = await self._register_and_login(client, "apt_iae@test.com")
        org_id = await self._create_org(client, token, "AptInactEmpOrg")

        emp_resp = await client.post(
            "/api/v1/employees",
            json={"organization_id": org_id, "name": "InactEmp", "email": "inact@test.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        emp_id = emp_resp.json()["id"]

        # Deactivate the employee
        await client.put(
            f"/api/v1/employees/{emp_id}",
            json={"is_active": False},
            headers={"Authorization": f"Bearer {token}"},
        )

        svc_resp = await client.post(
            "/api/v1/services",
            json={
                "organization_id": org_id,
                "name": "SvcIE",
                "price": "50.00",
                "duration_minutes": 30,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        svc_id = svc_resp.json()["id"]

        client_id = await self._create_client_direct(org_id, "clisie@test.com")

        now = datetime.now(UTC)
        response = await client.post(
            "/api/v1/appointments",
            json={
                "organization_id": org_id,
                "employee_id": emp_id,
                "client_id": client_id,
                "service_id": svc_id,
                "starts_at": (now + timedelta(hours=2)).isoformat(),
                "ends_at": (now + timedelta(hours=3)).isoformat(),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400
        assert "not active" in response.json()["detail"]
