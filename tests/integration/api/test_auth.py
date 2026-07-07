class TestAuthAPI:
    async def test_register_success(self, client):
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "newuser@example.com", "password": "StrongPass1"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["is_active"] is True
        assert "id" in data

    async def test_register_duplicate_email(self, client):
        await client.post(
            "/api/v1/auth/register",
            json={"email": "dup@example.com", "password": "Pass1234"},
        )
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "dup@example.com", "password": "Pass1234"},
        )
        assert response.status_code == 400
        data = response.json()
        assert "already registered" in data["detail"]

    async def test_login_success(self, client):
        await client.post(
            "/api/v1/auth/register",
            json={"email": "loginuser@example.com", "password": "SecurePass1"},
        )
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "loginuser@example.com", "password": "SecurePass1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "loginuser@example.com"
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_password(self, client):
        await client.post(
            "/api/v1/auth/register",
            json={"email": "badpass@example.com", "password": "RealPass1"},
        )
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "badpass@example.com", "password": "WrongPass1"},
        )
        assert response.status_code == 401
        data = response.json()
        assert "Invalid credentials" in data["detail"]

    async def test_login_nonexistent_user(self, client):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "SomePass1"},
        )
        assert response.status_code == 401

    async def test_me_authenticated(self, client):
        await client.post(
            "/api/v1/auth/register",
            json={"email": "meuser@example.com", "password": "AuthPass1"},
        )
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "meuser@example.com", "password": "AuthPass1"},
        )
        token = login_resp.json()["access_token"]

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "meuser@example.com"

    async def test_me_unauthenticated(self, client):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_me_invalid_token(self, client):
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401
