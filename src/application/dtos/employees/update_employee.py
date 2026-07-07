from dataclasses import dataclass


@dataclass
class UpdateEmployeeRequest:
    employee_id: str
    user_id: str
    name: str | None = None
    phone: str | None = None
    is_active: bool | None = None


@dataclass
class UpdateEmployeeResponse:
    id: str
    organization_id: str
    name: str
    email: str
    phone: str | None
    is_active: bool
