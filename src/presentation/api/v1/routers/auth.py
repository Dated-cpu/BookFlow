from fastapi import APIRouter, Depends, status

from src.application.dtos.auth.login_user import LoginUserRequest as LoginUserAppRequest
from src.application.dtos.auth.register_user import RegisterUserRequest as RegisterUserAppRequest
from src.application.use_cases.auth.login_user import LoginUser
from src.application.use_cases.auth.register_user import RegisterUser
from src.domain.entities.user import User
from src.presentation.api.v1.dependencies import (
    get_current_user,
    get_login_user_use_case,
    get_register_user_use_case,
)
from src.presentation.api.v1.schemas.auth import (
    LoginUserRequest,
    LoginUserResponse,
    RegisterUserRequest,
    RegisterUserResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=RegisterUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    body: RegisterUserRequest,
    use_case: RegisterUser = Depends(get_register_user_use_case),
) -> RegisterUserResponse:
    app_request = RegisterUserAppRequest(email=body.email, password=body.password)
    result = await use_case.execute(app_request)
    return RegisterUserResponse(
        id=result.id,
        email=result.email,
        is_active=result.is_active,
    )


@router.post(
    "/login",
    response_model=LoginUserResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    body: LoginUserRequest,
    use_case: LoginUser = Depends(get_login_user_use_case),
) -> LoginUserResponse:
    app_request = LoginUserAppRequest(email=body.email, password=body.password)
    result = await use_case.execute(app_request)
    return LoginUserResponse(
        id=result.id,
        email=result.email,
        is_active=result.is_active,
        access_token=result.access_token,
        token_type=result.token_type,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        is_active=current_user.is_active,
    )
