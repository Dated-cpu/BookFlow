from dataclasses import dataclass


@dataclass
class LoginUserRequest:
    email: str
    password: str


@dataclass
class LoginUserResponse:
    id: str
    email: str
    is_active: bool
    access_token: str
    token_type: str = "bearer"
