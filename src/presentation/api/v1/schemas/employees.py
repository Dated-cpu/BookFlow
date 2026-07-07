from pydantic import BaseModel


class EmployeeCreateRequest(BaseModel):
    organization_id: str
    name: str
    email: str
    phone: str | None = None


class EmployeeResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    email: str
    phone: str | None
    is_active: bool


class EmployeeUpdateRequest(BaseModel):
    name: str | None = None
    phone: str | None = None
    is_active: bool | None = None
