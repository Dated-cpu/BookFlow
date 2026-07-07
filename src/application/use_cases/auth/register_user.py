from src.application.base import BaseUseCase
from src.application.dtos.auth.register_user import (
    RegisterUserRequest,
    RegisterUserResponse,
)
from src.application.exceptions import ApplicationError
from src.application.ports.password_hasher import PasswordHasher
from src.application.ports.unit_of_work import UnitOfWork
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


class RegisterUser(BaseUseCase[RegisterUserRequest, RegisterUserResponse]):
    def __init__(
        self,
        user_repo: UserRepository,
        password_hasher: PasswordHasher,
        uow: UnitOfWork,
    ) -> None:
        self._user_repo = user_repo
        self._password_hasher = password_hasher
        self._uow = uow

    async def execute(self, request: RegisterUserRequest) -> RegisterUserResponse:
        existing = await self._user_repo.get_by_email(request.email)
        if existing:
            raise ApplicationError("Email already registered")

        hashed = self._password_hasher.hash(request.password)
        user = User(email=request.email, hashed_password=hashed)

        async with self._uow:
            saved = await self._user_repo.add(user)

        return RegisterUserResponse(
            id=str(saved.id),
            email=saved.email,
            is_active=saved.is_active,
        )
