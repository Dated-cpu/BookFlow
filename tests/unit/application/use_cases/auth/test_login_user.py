from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.dtos.auth.login_user import LoginUserRequest
from src.application.exceptions import AuthenticationError
from src.application.use_cases.auth.login_user import LoginUser
from src.domain.entities.user import User


class TestLoginUser:
    async def test_login_success(self, mock_user_repo, mock_password_hasher):
        user = User(email="alice@example.com", hashed_password="hashed_pass")
        mock_user_repo.get_by_email = AsyncMock(return_value=user)

        mock_token_service = MagicMock()
        mock_token_service.create_access_token = MagicMock(return_value="jwt.token.here")

        use_case = LoginUser(
            user_repo=mock_user_repo,
            password_hasher=mock_password_hasher,
            token_service=mock_token_service,
        )

        request = LoginUserRequest(email="alice@example.com", password="plainpass")
        response = await use_case.execute(request)

        assert response.email == "alice@example.com"
        assert response.access_token == "jwt.token.here"
        assert response.token_type == "bearer"
        mock_password_hasher.verify.assert_called_once_with("plainpass", "hashed_pass")
        mock_token_service.create_access_token.assert_called_once_with(
            payload={"sub": str(user.id)}
        )

    async def test_login_invalid_email(self, mock_user_repo, mock_password_hasher):
        mock_user_repo.get_by_email = AsyncMock(return_value=None)

        use_case = LoginUser(
            user_repo=mock_user_repo,
            password_hasher=mock_password_hasher,
            token_service=MagicMock(),
        )

        request = LoginUserRequest(email="nobody@example.com", password="pass")
        with pytest.raises(AuthenticationError, match="Invalid credentials"):
            await use_case.execute(request)

    async def test_login_wrong_password(self, mock_user_repo, mock_password_hasher):
        user = User(email="bob@example.com", hashed_password="real_hash")
        mock_user_repo.get_by_email = AsyncMock(return_value=user)
        mock_password_hasher.verify = MagicMock(return_value=False)

        use_case = LoginUser(
            user_repo=mock_user_repo,
            password_hasher=mock_password_hasher,
            token_service=MagicMock(),
        )

        request = LoginUserRequest(email="bob@example.com", password="wrong")
        with pytest.raises(AuthenticationError, match="Invalid credentials"):
            await use_case.execute(request)
