from src.application.base import BaseUseCase
from src.application.dtos.auth.login_user import LoginUserRequest, LoginUserResponse
from src.application.exceptions import AuthenticationError
from src.application.ports.password_hasher import PasswordHasher
from src.application.ports.token_service import TokenService
from src.domain.repositories.user_repository import UserRepository


class LoginUser(BaseUseCase[LoginUserRequest, LoginUserResponse]):
    def __init__(
        self,
        user_repo: UserRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self._user_repo = user_repo
        self._password_hasher = password_hasher
        self._token_service = token_service

    async def execute(self, request: LoginUserRequest) -> LoginUserResponse:
        user = await self._user_repo.get_by_email(request.email)
        if not user:
            raise AuthenticationError("Invalid credentials")

        if not self._password_hasher.verify(request.password, user.hashed_password):
            raise AuthenticationError("Invalid credentials")

        access_token = self._token_service.create_access_token(payload={"sub": str(user.id)})

        return LoginUserResponse(
            id=str(user.id),
            email=user.email,
            is_active=user.is_active,
            access_token=access_token,
        )
