class TestOrganizationsAPI:
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

    async def test_create_organization(self, client):
        token = await self._register_and_login(client, "create@test.com")

        response = await client.post(
            "/api/v1/organizations",
            json={"name": "My Test Org"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Test Org"
        assert data["slug"] == "my-test-org"
        assert "id" in data

    async def test_create_duplicate_name(self, client):
        token = await self._register_and_login(client, "dup@test.com")

        await client.post(
            "/api/v1/organizations",
            json={"name": "My Org"},
            headers={"Authorization": f"Bearer {token}"},
        )
        response = await client.post(
            "/api/v1/organizations",
            json={"name": "My Org"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    async def test_create_organization_requires_auth(self, client):
        response = await client.post(
            "/api/v1/organizations",
            json={"name": "No Auth Org"},
        )
        assert response.status_code == 401

    async def test_list_my_organizations(self, client):
        token = await self._register_and_login(client, "list@test.com")

        await client.post(
            "/api/v1/organizations",
            json={"name": "Org Alpha"},
            headers={"Authorization": f"Bearer {token}"},
        )
        await client.post(
            "/api/v1/organizations",
            json={"name": "Org Beta"},
            headers={"Authorization": f"Bearer {token}"},
        )

        response = await client.get(
            "/api/v1/organizations",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = {o["name"] for o in data}
        assert names == {"Org Alpha", "Org Beta"}
        for org in data:
            assert org["role"] == "owner"

    async def test_user_only_sees_own_orgs(self, client):
        token_a = await self._register_and_login(client, "user_a@test.com")
        token_b = await self._register_and_login(client, "user_b@test.com")

        await client.post(
            "/api/v1/organizations",
            json={"name": "A's Org"},
            headers={"Authorization": f"Bearer {token_a}"},
        )

        response_b = await client.get(
            "/api/v1/organizations",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert response_b.status_code == 200
        assert len(response_b.json()) == 0

        await client.post(
            "/api/v1/organizations",
            json={"name": "B's Org"},
            headers={"Authorization": f"Bearer {token_b}"},
        )

        response_b2 = await client.get(
            "/api/v1/organizations",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert len(response_b2.json()) == 1
        assert response_b2.json()[0]["name"] == "B's Org"

    async def test_get_organization_by_id(self, client):
        token = await self._register_and_login(client, "getbyid@test.com")

        create_resp = await client.post(
            "/api/v1/organizations",
            json={"name": "Get By ID Org"},
            headers={"Authorization": f"Bearer {token}"},
        )
        org_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/organizations/{org_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == org_id
        assert data["name"] == "Get By ID Org"
        assert data["is_active"] is True

    async def test_cannot_access_other_org(self, client):
        token_a = await self._register_and_login(client, "owner_a@test.com")
        token_b = await self._register_and_login(client, "owner_b@test.com")

        create_resp = await client.post(
            "/api/v1/organizations",
            json={"name": "A's Private Org"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        org_a_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/organizations/{org_a_id}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]

    async def test_get_organization_not_found(self, client):
        token = await self._register_and_login(client, "notfound@test.com")
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = await client.get(
            f"/api/v1/organizations/{fake_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]
