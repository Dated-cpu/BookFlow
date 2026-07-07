from pydantic import BaseModel, EmailStr


class RegisterUserRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterUserResponse(BaseModel):
    id: str
    email: str
    is_active: bool


class LoginUserRequest(BaseModel):
    email: EmailStr
    password: str


class LoginUserResponse(BaseModel):
    id: str
    email: str
    is_active: bool
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    is_active: bool
