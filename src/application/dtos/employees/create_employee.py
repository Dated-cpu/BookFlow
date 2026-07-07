from dataclasses import dataclass


@dataclass
class CreateEmployeeRequest:
    organization_id: str
    owner_user_id: str
    name: str
    email: str
    phone: str | None = None


@dataclass
class EmployeeResponse:
    id: str
    organization_id: str
    name: str
    email: str
    phone: str | None
    is_active: bool
