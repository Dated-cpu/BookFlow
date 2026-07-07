from dataclasses import dataclass
from decimal import Decimal


@dataclass
class UpdateServiceRequest:
    service_id: str
    user_id: str
    name: str | None = None
    price: Decimal | None = None
    duration_minutes: int | None = None
    description: str | None = None
    is_active: bool | None = None


@dataclass
class UpdateServiceResponse:
    id: str
    organization_id: str
    name: str
    price: Decimal
    duration_minutes: int
    description: str | None
    is_active: bool
