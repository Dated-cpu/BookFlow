class TestEmployeesAPI:
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

    async def test_create_employee(self, client):
        token = await self._register_and_login(client, "emp_create@test.com")
        org_id = await self._create_org(client, token, "EmpCreateOrg")

        response = await client.post(
            "/api/v1/employees",
            json={
                "organization_id": org_id,
                "name": "Alice",
                "email": "alice@test.com",
                "phone": "+123456789",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Alice"
        assert data["email"] == "alice@test.com"
        assert data["phone"] == "+123456789"
        assert data["is_active"] is True
        assert data["organization_id"] == org_id

    async def test_create_employee_duplicate_email(self, client):
        token = await self._register_and_login(client, "emp_dup@test.com")
        org_id = await self._create_org(client, token, "DupOrg")

        await client.post(
            "/api/v1/employees",
            json={
                "organization_id": org_id,
                "name": "Bob",
                "email": "bob@test.com",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        response = await client.post(
            "/api/v1/employees",
            json={
                "organization_id": org_id,
                "name": "Bob Again",
                "email": "bob@test.com",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    async def test_list_employees(self, client):
        token = await self._register_and_login(client, "emp_list@test.com")
        org_id = await self._create_org(client, token, "ListOrg")

        await client.post(
            "/api/v1/employees",
            json={"organization_id": org_id, "name": "Emp1", "email": "emp1@test.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        await client.post(
            "/api/v1/employees",
            json={"organization_id": org_id, "name": "Emp2", "email": "emp2@test.com"},
            headers={"Authorization": f"Bearer {token}"},
        )

        response = await client.get(
            f"/api/v1/employees?organization_id={org_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = {e["name"] for e in data}
        assert names == {"Emp1", "Emp2"}

    async def test_list_employees_other_org(self, client):
        token_a = await self._register_and_login(client, "list_a@test.com")
        token_b = await self._register_and_login(client, "list_b@test.com")

        org_a = await self._create_org(client, token_a, "OrgA")
        await self._create_org(client, token_b, "OrgB")

        await client.post(
            "/api/v1/employees",
            json={"organization_id": org_a, "name": "A Employee", "email": "a@test.com"},
            headers={"Authorization": f"Bearer {token_a}"},
        )

        # User B should not see A's employees
        response = await client.get(
            f"/api/v1/employees?organization_id={org_a}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]

    async def test_get_employee_by_id(self, client):
        token = await self._register_and_login(client, "emp_get@test.com")
        org_id = await self._create_org(client, token, "GetOrg")

        create_resp = await client.post(
            "/api/v1/employees",
            json={"organization_id": org_id, "name": "Charlie", "email": "charlie@test.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        emp_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/employees/{emp_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == emp_id
        assert data["name"] == "Charlie"

    async def test_get_employee_from_other_org(self, client):
        token_a = await self._register_and_login(client, "get_a@test.com")
        token_b = await self._register_and_login(client, "get_b@test.com")

        org_a = await self._create_org(client, token_a, "GetOrgA")

        create_resp = await client.post(
            "/api/v1/employees",
            json={"organization_id": org_a, "name": "Secret", "email": "secret@test.com"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        emp_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/employees/{emp_id}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]

    async def test_update_employee(self, client):
        token = await self._register_and_login(client, "emp_upd@test.com")
        org_id = await self._create_org(client, token, "UpdOrg")

        create_resp = await client.post(
            "/api/v1/employees",
            json={"organization_id": org_id, "name": "Diana", "email": "diana@test.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        emp_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/employees/{emp_id}",
            json={"name": "Diana Updated", "phone": "+999", "is_active": False},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Diana Updated"
        assert data["phone"] == "+999"
        assert data["is_active"] is False

    async def test_delete_employee_soft(self, client):
        token = await self._register_and_login(client, "emp_del@test.com")
        org_id = await self._create_org(client, token, "DelOrg")

        create_resp = await client.post(
            "/api/v1/employees",
            json={"organization_id": org_id, "name": "Eve", "email": "eve@test.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        emp_id = create_resp.json()["id"]

        delete_resp = await client.delete(
            f"/api/v1/employees/{emp_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert delete_resp.status_code == 204

        # Verify employee is deactivated
        get_resp = await client.get(
            f"/api/v1/employees/{emp_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["is_active"] is False
