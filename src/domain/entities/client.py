import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from src.domain.base import BaseEntity


@dataclass(kw_only=True)
class Client(BaseEntity):
    organization_id: uuid.UUID
    name: str
    email: str
    phone: str | None = None
    notes: str | None = None

    def change_phone(self, new_phone: str) -> None:
        self.phone = new_phone
        self.updated_at = datetime.now(UTC)
