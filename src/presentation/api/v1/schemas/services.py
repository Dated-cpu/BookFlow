from decimal import Decimal

from pydantic import BaseModel


class ServiceCreateRequest(BaseModel):
    organization_id: str
    name: str
    price: Decimal
    duration_minutes: int
    description: str | None = None


class ServiceResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    price: Decimal
    duration_minutes: int
    description: str | None
    is_active: bool


class ServiceUpdateRequest(BaseModel):
    name: str | None = None
    price: Decimal | None = None
    duration_minutes: int | None = None
    description: str | None = None
    is_active: bool | None = None
