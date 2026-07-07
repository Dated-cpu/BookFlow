import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from src.domain.base import BaseEntity


@dataclass(kw_only=True)
class Employee(BaseEntity):
    organization_id: uuid.UUID
    name: str
    email: str
    phone: str | None = None
    user_id: uuid.UUID | None = None
    is_active: bool = True

    def activate(self) -> None:
        self.is_active = True
        self.updated_at = datetime.now(UTC)

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now(UTC)
