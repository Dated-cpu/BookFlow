from dataclasses import dataclass
from datetime import UTC, datetime

from src.domain.base import BaseEntity


@dataclass(kw_only=True)
class Organization(BaseEntity):
    name: str
    slug: str
    is_active: bool = True

    def rename(self, new_name: str) -> None:
        if not new_name or not new_name.strip():
            raise ValueError("Organization name cannot be empty")
        self.name = new_name.strip()
        self.updated_at = datetime.now(UTC)
