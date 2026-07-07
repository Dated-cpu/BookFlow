from unittest.mock import AsyncMock

import pytest

from src.application.dtos.auth.register_user import RegisterUserRequest
from src.application.exceptions import ApplicationError
from src.application.use_cases.auth.register_user import RegisterUser
from src.domain.entities.user import User


class TestRegisterUser:
    async def test_register_success(self, mock_user_repo, mock_password_hasher, mock_uow):
        mock_user_repo.get_by_email = AsyncMock(return_value=None)

        created_user = User(email="new@example.com", hashed_password="hashed_password")
        mock_user_repo.add = AsyncMock(return_value=created_user)

        use_case = RegisterUser(
            user_repo=mock_user_repo,
            password_hasher=mock_password_hasher,
            uow=mock_uow,
        )

        request = RegisterUserRequest(email="new@example.com", password="plainpass")
        response = await use_case.execute(request)

        assert response.email == "new@example.com"
        assert response.is_active is True
        assert response.id == str(created_user.id)

        mock_user_repo.get_by_email.assert_awaited_once_with("new@example.com")
        mock_password_hasher.hash.assert_called_once_with("plainpass")
        mock_user_repo.add.assert_awaited_once()

    async def test_register_duplicate_email(self, mock_user_repo, mock_password_hasher, mock_uow):
        existing = User(email="dup@example.com", hashed_password="hash")
        mock_user_repo.get_by_email = AsyncMock(return_value=existing)

        use_case = RegisterUser(
            user_repo=mock_user_repo,
            password_hasher=mock_password_hasher,
            uow=mock_uow,
        )

        request = RegisterUserRequest(email="dup@example.com", password="pass")
        with pytest.raises(ApplicationError, match="already registered"):
            await use_case.execute(request)

        mock_user_repo.add.assert_not_called()
