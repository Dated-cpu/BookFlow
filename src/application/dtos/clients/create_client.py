from dataclasses import dataclass


@dataclass
class CreateClientRequest:
    organization_id: str
    name: str
    email: str
    phone: str | None = None


@dataclass
class CreateClientResponse:
    id: str
    organization_id: str
    name: str
    email: str
    phone: str | None
