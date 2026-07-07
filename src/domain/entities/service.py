import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from src.domain.base import BaseEntity


@dataclass(kw_only=True)
class Service(BaseEntity):
    organization_id: uuid.UUID
    name: str
    price: Decimal
    duration_minutes: int
    description: str | None = None
    is_active: bool = True

    def __post_init__(self) -> None:
        if self.price < 0:
            raise ValueError("Price cannot be negative")
        if self.duration_minutes < 1:
            raise ValueError("Duration must be at least 1 minute")

    def change_price(self, new_price: Decimal) -> None:
        if new_price < 0:
            raise ValueError("Price cannot be negative")
        self.price = new_price
        self.updated_at = datetime.now(UTC)
