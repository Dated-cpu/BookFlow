from dataclasses import dataclass
from decimal import Decimal


@dataclass
class CreateServiceRequest:
    organization_id: str
    owner_user_id: str
    name: str
    price: Decimal
    duration_minutes: int
    description: str | None = None


@dataclass
class ServiceResponse:
    id: str
    organization_id: str
    name: str
    price: Decimal
    duration_minutes: int
    description: str | None
    is_active: bool
