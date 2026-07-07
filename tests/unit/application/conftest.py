from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_uow():
    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    return uow


@pytest.fixture
def mock_user_repo():
    return AsyncMock()


@pytest.fixture
def mock_org_repo():
    return AsyncMock()


@pytest.fixture
def mock_org_member_repo():
    return AsyncMock()


@pytest.fixture
def mock_employee_repo():
    return AsyncMock()


@pytest.fixture
def mock_service_repo():
    return AsyncMock()


@pytest.fixture
def mock_client_repo():
    return AsyncMock()


@pytest.fixture
def mock_appointment_repo():
    return AsyncMock()


@pytest.fixture
def mock_password_hasher():
    hasher = MagicMock()
    hasher.hash = MagicMock(return_value="hashed_password")
    hasher.verify = MagicMock(return_value=True)
    return hasher
