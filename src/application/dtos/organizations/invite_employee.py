from dataclasses import dataclass


@dataclass
class InviteEmployeeRequest:
    organization_id: str
    name: str
    email: str
    phone: str | None = None


@dataclass
class InviteEmployeeResponse:
    id: str
    organization_id: str
    name: str
    email: str
    phone: str | None
