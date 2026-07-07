from dataclasses import dataclass


@dataclass
class RegisterUserRequest:
    email: str
    password: str


@dataclass
class RegisterUserResponse:
    id: str
    email: str
    is_active: bool
