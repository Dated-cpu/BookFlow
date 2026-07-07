class TestServicesAPI:
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

    async def test_create_service(self, client):
        token = await self._register_and_login(client, "svc_create@test.com")
        org_id = await self._create_org(client, token, "SvcCreateOrg")

        response = await client.post(
            "/api/v1/services",
            json={
                "organization_id": org_id,
                "name": "Consulting",
                "price": "150.00",
                "duration_minutes": 60,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Consulting"
        assert data["price"] == "150.00"
        assert data["duration_minutes"] == 60
        assert data["is_active"] is True

    async def test_create_service_duplicate_name(self, client):
        token = await self._register_and_login(client, "svc_dup@test.com")
        org_id = await self._create_org(client, token, "SvcDupOrg")

        await client.post(
            "/api/v1/services",
            json={
                "organization_id": org_id,
                "name": "Massage",
                "price": "80.00",
                "duration_minutes": 45,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        response = await client.post(
            "/api/v1/services",
            json={
                "organization_id": org_id,
                "name": "Massage",
                "price": "90.00",
                "duration_minutes": 30,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    async def test_list_services(self, client):
        token = await self._register_and_login(client, "svc_list@test.com")
        org_id = await self._create_org(client, token, "SvcListOrg")

        await client.post(
            "/api/v1/services",
            json={
                "organization_id": org_id,
                "name": "Service A",
                "price": "50.00",
                "duration_minutes": 30,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        await client.post(
            "/api/v1/services",
            json={
                "organization_id": org_id,
                "name": "Service B",
                "price": "100.00",
                "duration_minutes": 60,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        response = await client.get(
            f"/api/v1/services?organization_id={org_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = {s["name"] for s in data}
        assert names == {"Service A", "Service B"}

    async def test_list_services_other_org(self, client):
        token_a = await self._register_and_login(client, "svc_a@test.com")
        token_b = await self._register_and_login(client, "svc_b@test.com")

        org_a = await self._create_org(client, token_a, "SvcOrgA")
        await self._create_org(client, token_b, "SvcOrgB")

        await client.post(
            "/api/v1/services",
            json={
                "organization_id": org_a,
                "name": "A Service",
                "price": "25.00",
                "duration_minutes": 20,
            },
            headers={"Authorization": f"Bearer {token_a}"},
        )

        response = await client.get(
            f"/api/v1/services?organization_id={org_a}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]

    async def test_get_service_by_id(self, client):
        token = await self._register_and_login(client, "svc_get@test.com")
        org_id = await self._create_org(client, token, "SvcGetOrg")

        create_resp = await client.post(
            "/api/v1/services",
            json={
                "organization_id": org_id,
                "name": "Haircut",
                "price": "35.00",
                "duration_minutes": 30,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        svc_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/services/{svc_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == svc_id
        assert data["name"] == "Haircut"

    async def test_get_service_from_other_org(self, client):
        token_a = await self._register_and_login(client, "sget_a@test.com")
        token_b = await self._register_and_login(client, "sget_b@test.com")

        org_a = await self._create_org(client, token_a, "SvcGetOrgA")

        create_resp = await client.post(
            "/api/v1/services",
            json={
                "organization_id": org_a,
                "name": "Secret Service",
                "price": "999.00",
                "duration_minutes": 120,
            },
            headers={"Authorization": f"Bearer {token_a}"},
        )
        svc_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/services/{svc_id}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]

    async def test_update_service(self, client):
        token = await self._register_and_login(client, "svc_upd@test.com")
        org_id = await self._create_org(client, token, "SvcUpdOrg")

        create_resp = await client.post(
            "/api/v1/services",
            json={
                "organization_id": org_id,
                "name": "Old Name",
                "price": "100.00",
                "duration_minutes": 60,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        svc_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/services/{svc_id}",
            json={
                "name": "New Name",
                "price": "200.00",
                "duration_minutes": 90,
                "is_active": False,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["price"] == "200.00"
        assert data["duration_minutes"] == 90
        assert data["is_active"] is False

    async def test_delete_service_soft(self, client):
        token = await self._register_and_login(client, "svc_del@test.com")
        org_id = await self._create_org(client, token, "SvcDelOrg")

        create_resp = await client.post(
            "/api/v1/services",
            json={
                "organization_id": org_id,
                "name": "To Delete",
                "price": "50.00",
                "duration_minutes": 30,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        svc_id = create_resp.json()["id"]

        delete_resp = await client.delete(
            f"/api/v1/services/{svc_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert delete_resp.status_code == 204

        get_resp = await client.get(
            f"/api/v1/services/{svc_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["is_active"] is False
